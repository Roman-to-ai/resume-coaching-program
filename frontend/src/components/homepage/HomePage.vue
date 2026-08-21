<script setup>
import Navbar from './Navbar.vue';
import AnnouncementBanner from './AnnouncementBanner.vue';
import HeroSection from './HeroSection.vue';
import FeatureCard from './FeatureCard.vue';
import RecruitCard from './RecruitCard.vue';
</script>

<template>
  <div class="home-page">
    <Navbar />

    <main class="main-content">
      <div class="content-wrapper">
        <div class="left-column">
          <AnnouncementBanner
            message="DeepSeek-V4-Pro 正式版发布，Agent 能力大幅提升，支持 Responses API 和 Codex 接入，已在网页端、APP 和 API 全面上线，欢迎测试和反馈"
            link="https://api-docs.deepseek.com/zh-cn/updates/"
          />

          <HeroSection title="探索未至之境" />

          <div class="feature-cards">
            <FeatureCard
              title="开始对话"
              description="与 DeepSeek 免费对话"
              sub-description="体验全新旗舰模型"
            />
            <FeatureCard
              title="API 开放平台"
              description="调用 DeepSeek 最新模型"
              sub-description="快速集成、流畅体验"
            />
          </div>
        </div>

        <div class="right-column">
          <RecruitCard
            title="加入 DeepSeek"
            subtitle="共赴星辰大海"
            link-text="查看岗位"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #eef2f9 0%, #f5f7fa 40%, #f5f7fa 100%);
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
}

.content-wrapper {
  display: flex;
  gap: 40px;
  align-items: flex-start;
}

.left-column {
  flex: 1;
  min-width: 0;
}

.right-column {
  flex-shrink: 0;
  padding-top: 40px;
}

.feature-cards {
  display: flex;
  gap: 20px;
  margin-top: 32px;
}

@media (max-width: 960px) {
  .content-wrapper {
    flex-direction: column;
  }

  .right-column {
    padding-top: 0;
    display: flex;
    justify-content: center;
  }

  .feature-cards {
    flex-direction: column;
  }

  .main-content {
    padding: 0 20px;
  }
}
</style>
