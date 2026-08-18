package com.carelens.backend.controller;

import com.carelens.backend.dto.JobDetail;
import com.carelens.backend.dto.JobListResponse;
import com.carelens.backend.service.JobService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/jobs")
public class JobController {

    private final JobService jobService;

    public JobController(JobService jobService) {
        this.jobService = jobService;
    }

    @GetMapping
    public JobListResponse list(
            @RequestParam(required = false) String keyword,
            @RequestParam(required = false) String experience,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        return jobService.list(keyword, experience, page, size);
    }

    @GetMapping("/{jobId}")
    public JobDetail detail(@PathVariable String jobId) {
        return jobService.detail(jobId);
    }
}
