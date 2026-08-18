package com.carelens.backend.dto;

/** 岗位详情（含完整描述）。 */
public record JobDetail(
        String jobId,
        String title,
        String company,
        String salary,
        String location,
        String experience,
        String degree,
        String skills,
        String companyIndustry,
        String description,
        String companyScale,
        String companyStage,
        String welfare,
        String url) {
}
