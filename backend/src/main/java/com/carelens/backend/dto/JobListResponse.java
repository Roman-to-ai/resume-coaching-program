package com.carelens.backend.dto;

import java.util.List;

public record JobListResponse(long total, int page, int size, List<JobSummary> items) {
}
