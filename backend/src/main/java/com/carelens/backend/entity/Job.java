package com.carelens.backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "jobs")
public class Job {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "job_id", unique = true, nullable = false)
    private String jobId;

    private String title;
    private String company;
    private String salary;
    private String location;
    private String experience;
    private String degree;

    @Column(length = 1024)
    private String skills;

    @Column(columnDefinition = "MEDIUMTEXT")
    private String description;

    @Column(name = "company_scale")
    private String companyScale;

    @Column(name = "company_stage")
    private String companyStage;

    @Column(name = "company_industry")
    private String companyIndustry;

    @Column(columnDefinition = "TEXT")
    private String welfare;

    private String url;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getJobId() { return jobId; }
    public void setJobId(String jobId) { this.jobId = jobId; }
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    public String getCompany() { return company; }
    public void setCompany(String company) { this.company = company; }
    public String getSalary() { return salary; }
    public void setSalary(String salary) { this.salary = salary; }
    public String getLocation() { return location; }
    public void setLocation(String location) { this.location = location; }
    public String getExperience() { return experience; }
    public void setExperience(String experience) { this.experience = experience; }
    public String getDegree() { return degree; }
    public void setDegree(String degree) { this.degree = degree; }
    public String getSkills() { return skills; }
    public void setSkills(String skills) { this.skills = skills; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getCompanyScale() { return companyScale; }
    public void setCompanyScale(String companyScale) { this.companyScale = companyScale; }
    public String getCompanyStage() { return companyStage; }
    public void setCompanyStage(String companyStage) { this.companyStage = companyStage; }
    public String getCompanyIndustry() { return companyIndustry; }
    public void setCompanyIndustry(String companyIndustry) { this.companyIndustry = companyIndustry; }
    public String getWelfare() { return welfare; }
    public void setWelfare(String welfare) { this.welfare = welfare; }
    public String getUrl() { return url; }
    public void setUrl(String url) { this.url = url; }
}
