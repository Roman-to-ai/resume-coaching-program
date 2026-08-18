package com.carelens.backend.config;

import com.carelens.backend.entity.Job;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Component;

/**
 * 将抓取的「岗位概要 JSON + 详情 JSON」合并为完整 Job 实体。
 * 概要文件：{ "jobs": [ { job_id, title, ..., company_scale, job_link, ... } ] }
 * 详情文件：{ "<job_id>": { title, ..., url, description } }
 *
 * 设计为纯解析类（无 Spring 上下文依赖），便于单元测试。
 */
@Component
public class JdDataParser {

    private final ObjectMapper mapper = new ObjectMapper();

    public List<Job> mergeBand(String summaryJson, String detailsJson) {
        List<Job> jobs = new ArrayList<>();
        try {
            JsonNode detailMap = mapper.readTree(detailsJson);
            JsonNode jobArray = mapper.readTree(summaryJson).path("jobs");
            for (JsonNode s : jobArray) {
                String jobId = s.path("job_id").asText(null);
                if (jobId == null || jobId.isBlank()) {
                    continue;
                }
                JsonNode d = detailMap.path(jobId);

                Job job = new Job();
                job.setJobId(jobId);
                job.setTitle(s.path("title").asText(null));
                job.setCompany(s.path("company").asText(null));
                job.setSalary(s.path("salary").asText(null));
                job.setLocation(s.path("location").asText(null));
                job.setExperience(s.path("experience").asText(null));
                job.setDegree(s.path("degree").asText(null));
                job.setSkills(s.path("skills").asText(null));
                job.setDescription(d.path("description").asText(null));
                job.setCompanyScale(s.path("company_scale").asText(null));
                job.setCompanyStage(s.path("company_stage").asText(null));
                job.setCompanyIndustry(s.path("company_industry").asText(null));
                job.setWelfare(s.path("welfare").asText(null));

                String url = d.path("url").asText(null);
                if (url == null || url.isBlank()) {
                    url = s.path("job_link").asText(null);
                }
                job.setUrl(url);
                jobs.add(job);
            }
        } catch (Exception e) {
            throw new IllegalStateException("解析 JD 数据失败: " + e.getMessage(), e);
        }
        return jobs;
    }
}
