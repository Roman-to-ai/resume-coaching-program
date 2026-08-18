package com.carelens.backend.dto;

/** 分析请求：简历文本 + 所选岗位。 */
public record AnalyzeRequest(String resumeText, String jobId) {
}
