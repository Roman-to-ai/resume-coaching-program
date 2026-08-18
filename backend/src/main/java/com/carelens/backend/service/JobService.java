package com.carelens.backend.service;

import com.carelens.backend.dto.JobDetail;
import com.carelens.backend.dto.JobListResponse;
import com.carelens.backend.dto.JobSummary;
import com.carelens.backend.entity.Job;
import com.carelens.backend.repository.JobRepository;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

@Service
public class JobService {

    private final JobRepository repository;

    public JobService(JobRepository repository) {
        this.repository = repository;
    }

    /** 分页/关键词/经验筛选的岗位列表。 */
    public JobListResponse list(String keyword, String experience, int page, int size) {
        Page<Job> result = repository.search(
                normalize(keyword), normalize(experience), PageRequest.of(page - 1, size));
        List<JobSummary> items = result.getContent().stream().map(this::toSummary).toList();
        return new JobListResponse(result.getTotalElements(), page, size, items);
    }

    public JobDetail detail(String jobId) {
        Job job = repository.findByJobId(jobId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "岗位不存在: " + jobId));
        return toDetail(job);
    }

    Job findEntity(String jobId) {
        return repository.findByJobId(jobId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "岗位不存在: " + jobId));
    }

    private JobSummary toSummary(Job j) {
        return new JobSummary(j.getJobId(), j.getTitle(), j.getCompany(), j.getSalary(),
                j.getLocation(), j.getExperience(), j.getDegree(), j.getSkills(), j.getCompanyIndustry());
    }

    private JobDetail toDetail(Job j) {
        return new JobDetail(j.getJobId(), j.getTitle(), j.getCompany(), j.getSalary(),
                j.getLocation(), j.getExperience(), j.getDegree(), j.getSkills(), j.getCompanyIndustry(),
                j.getDescription(), j.getCompanyScale(), j.getCompanyStage(), j.getWelfare(), j.getUrl());
    }

    private String normalize(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        return value.trim();
    }
}
