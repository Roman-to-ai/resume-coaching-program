package com.carelens.backend.config;

import com.carelens.backend.dto.ErrorResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<ErrorResponse> handleStatus(ResponseStatusException e) {
        String code = switch (e.getStatusCode().value()) {
            case 400 -> "BAD_REQUEST";
            case 404 -> "NOT_FOUND";
            case 502 -> "UPSTREAM_ERROR";
            default -> "ERROR";
        };
        return ResponseEntity.status(e.getStatusCode())
                .body(new ErrorResponse(code, e.getReason()));
    }
}
