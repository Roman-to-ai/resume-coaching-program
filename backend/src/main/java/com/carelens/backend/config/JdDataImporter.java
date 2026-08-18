package com.carelens.backend.config;

import com.carelens.backend.entity.Job;
import com.carelens.backend.repository.JobRepository;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.stereotype.Component;

/**
 * 启动时若 jobs 表为空，则从 classpath:jd-data/ 导入岗位数据。
 * 数据来自 data/fixtures/jd/ 抓取结果（概要 + 详情成对文件）。
 */
@Component
public class JdDataImporter implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(JdDataImporter.class);
    private static final String[] BANDS = {"1-3年", "3-5年", "5-10年"};

    private final JobRepository repository;
    private final JdDataParser parser;

    public JdDataImporter(JobRepository repository, JdDataParser parser) {
        this.repository = repository;
        this.parser = parser;
    }

    @Override
    public void run(String... args) {
        if (repository.count() > 0) {
            log.info("jobs 表已有 {} 条数据，跳过导入", repository.count());
            return;
        }

        List<Job> all = new ArrayList<>();
        for (String band : BANDS) {
            all.addAll(parser.mergeBand(read("jd-data/" + band + ".json"), read("jd-data/" + band + "_details.json")));
        }
        repository.saveAll(all);
        log.info("已导入 {} 条岗位数据", all.size());
    }

    private String read(String location) {
        try {
            Resource resource = new PathMatchingResourcePatternResolver().getResource("classpath:" + location);
            return new String(resource.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        } catch (IOException e) {
            throw new IllegalStateException("读取 JD 资源失败: " + location, e);
        }
    }
}
