package com.carelens.backend.controller;

import com.carelens.backend.dto.AnalyzeRequest;
import com.carelens.backend.service.AnalyzeService;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1")
public class AnalyzeController {

    private final AnalyzeService analyzeService;

    public AnalyzeController(AnalyzeService analyzeService) {
        this.analyzeService = analyzeService;
    }

    @PostMapping("/analyze")
    public Object analyze(@RequestBody AnalyzeRequest request) {
        return analyzeService.analyze(request);
    }
}
