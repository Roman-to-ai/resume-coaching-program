package com.carelens.backend.config;

import static org.assertj.core.api.Assertions.assertThat;

import com.carelens.backend.entity.Job;
import java.nio.charset.StandardCharsets;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;

/** 不依赖 Spring 上下文与 MySQL 的解析单测，直接读取 classpath 资源。 */
class JdDataParserTest {

    private final JdDataParser parser = new JdDataParser();

    @Test
    void mergeBand_combinesSummaryAndDetails() throws Exception {
        String summary = read("jd-data/1-3年.json");
        String details = read("jd-data/1-3年_details.json");

        List<Job> jobs = parser.mergeBand(summary, details);

        assertThat(jobs).isNotEmpty();
        Job first = jobs.get(0);
        assertThat(first.getJobId()).isNotBlank();
        assertThat(first.getTitle()).isNotBlank();
        assertThat(first.getDescription()).isNotBlank();
        assertThat(first.getCompanyIndustry()).isNotNull();
    }

    private String read(String location) throws Exception {
        return new String(new ClassPathResource(location).getInputStream().readAllBytes(), StandardCharsets.UTF_8);
    }
}
