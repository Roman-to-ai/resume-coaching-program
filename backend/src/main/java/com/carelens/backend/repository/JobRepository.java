package com.carelens.backend.repository;

import com.carelens.backend.entity.Job;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface JobRepository extends JpaRepository<Job, Long> {

    Optional<Job> findByJobId(String jobId);

    @Query("""
            SELECT j FROM Job j
            WHERE (:keyword IS NULL OR :keyword = ''
                   OR j.title LIKE %:keyword% OR j.company LIKE %:keyword% OR j.skills LIKE %:keyword%)
              AND (:experience IS NULL OR :experience = '' OR j.experience = :experience)
            """)
    Page<Job> search(@Param("keyword") String keyword,
                     @Param("experience") String experience,
                     Pageable pageable);
}
