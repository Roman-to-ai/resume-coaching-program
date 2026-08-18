package com.carelens.backend.dto;

/** 岗位列表项（不含 description，减小列表体积）。 */
public record JobSummary(
        String jobId,
        String title,
        String company,
        String salary,
        String location,
        String experience,
        String degree,
        String skills,
        String companyIndustry) {
}
