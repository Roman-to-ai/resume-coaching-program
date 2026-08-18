package com.carelens.backend;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.carelens.backend.repository.JobRepository;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.client.RestTemplate;

/**
 * 以 H2 内存库替代 MySQL 做集成验证：
 * 1) 启动时 JD 数据导入；2) 岗位列表/详情接口；3) snake_case 请求反序列化 + 分析编排透传。
 */
@SpringBootTest(properties = {
        "spring.datasource.url=jdbc:h2:mem:careerlens;MODE=MySQL;DB_CLOSE_DELAY=-1;DATABASE_TO_LOWER=TRUE",
        "spring.datasource.driver-class-name=org.h2.Driver",
        "spring.datasource.username=sa",
        "spring.datasource.password=",
        "spring.jpa.hibernate.ddl-auto=create-drop",
        "spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.H2Dialect",
})
@AutoConfigureMockMvc
class BackendIntegrationTest {

    @Autowired
    MockMvc mockMvc;

    @Autowired
    JobRepository repository;

    @MockBean
    RestTemplate restTemplate;

    @Test
    void jdDataIsImportedOnStartup() {
        assertThat(repository.count()).isGreaterThan(100);
    }

    @Test
    void listJobsReturnsSnakeCaseSummary() throws Exception {
        mockMvc.perform(get("/api/v1/jobs").param("size", "3"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.total").isNumber())
                .andExpect(jsonPath("$.items").isArray())
                .andExpect(jsonPath("$.items[0].job_id").isNotEmpty())
                .andExpect(jsonPath("$.items[0].title").isNotEmpty());
    }

    @Test
    void detailReturnsFullFields() throws Exception {
        String jobId = repository.findAll().get(0).getJobId();
        mockMvc.perform(get("/api/v1/jobs/{id}", jobId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.job_id").value(jobId))
                .andExpect(jsonPath("$.description").isNotEmpty());
    }

    @Test
    void analyzeDeserializesSnakeCaseAndPassesThrough() throws Exception {
        Map<String, Object> canned = new HashMap<>();
        canned.put("match_score", 85);
        canned.put("level", "high");
        canned.put("hits", List.of());
        canned.put("gaps", List.of());
        canned.put("degree_match", true);
        canned.put("experience_match", true);
        when(restTemplate.postForObject(eq("http://localhost:8001/api/v1/analyze"), any(), eq(Map.class)))
                .thenReturn(canned);

        String jobId = repository.findAll().get(0).getJobId();
        String body = "{\"resume_text\":\"Java、Spring Boot、MySQL\",\"job_id\":\"" + jobId + "\"}";
        mockMvc.perform(post("/api/v1/analyze").contentType(MediaType.APPLICATION_JSON).content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.match_score").value(85))
                .andExpect(jsonPath("$.level").value("high"));
    }
}
