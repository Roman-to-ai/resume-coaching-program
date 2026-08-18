package com.carelens.backend.service;

import com.carelens.backend.dto.AnalyzeRequest;
import com.carelens.backend.entity.Job;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;

@Service
public class AnalyzeService {

    private final JobService jobService;
    private final RestTemplate restTemplate;

    @Value("${carelens.ai-service-url}")
    private String aiServiceUrl;

    public AnalyzeService(JobService jobService, RestTemplate restTemplate) {
        this.jobService = jobService;
        this.restTemplate = restTemplate;
    }

    /**
     * 组装简历 + 岗位，调用 Python AI 服务，并把其 MatchResult 原样透传。
     * Python 返回已是 snake_case，因此这里直接返回 Map 保持字段命名一致。
     */
    public Object analyze(AnalyzeRequest request) {
        if (request.resumeText() == null || request.resumeText().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "简历文本不能为空");
        }
        if (request.jobId() == null || request.jobId().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "job_id 不能为空");
        }

        Job job = jobService.findEntity(request.jobId());

        Map<String, Object> payload = Map.of(
                "resume_text", request.resumeText(),
                "job", Map.of(
                        "job_id", job.getJobId(),
                        "title", job.getTitle(),
                        "skills", job.getSkills(),
                        "description", job.getDescription(),
                        "experience", job.getExperience(),
                        "degree", job.getDegree()));

        try {
            return restTemplate.postForObject(aiServiceUrl + "/api/v1/analyze", payload, Map.class);
        } catch (RestClientException e) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "AI 服务调用失败: " + e.getMessage());
        }
    }
}
