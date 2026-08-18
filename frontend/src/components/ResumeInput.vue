<script setup>
import { ref } from 'vue';
import { extractPdf } from '../api';

const props = defineProps({ modelValue: String });
const emit = defineEmits(['update:modelValue']);

const fileInput = ref(null);
const extracting = ref(false);

const SAMPLE = `张三
求职意向：Java 后端开发工程师

教育背景
- 2016.09 - 2020.06  广东工业大学  计算机科学与技术  本科

工作经历
- 2020.07 - 2023.06  某互联网公司  Java 开发工程师
  负责电商订单系统，使用 Spring Boot、MySQL、Redis、MyBatis 开发；
  参与微服务拆分，熟悉 RabbitMQ 消息队列与 Docker 容器化部署。

项目经历
- 订单中心重构：将单体拆分为订单、库存两个微服务，接口耗时降低 40%。

技能
Java、Spring Boot、Spring Cloud、MyBatis、MySQL、Redis、RabbitMQ、Docker、Git、Linux`;

function loadSample() {
  emit('update:modelValue', SAMPLE);
}

function onPickPdf(e) {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  extracting.value = true;
  extractPdf(file)
    .then((text) => emit('update:modelValue', text))
    .catch((err) => alert(`PDF 解析失败：${err.message}`))
    .finally(() => {
      extracting.value = false;
      if (fileInput.value) fileInput.value.value = '';
    });
}
</script>

<template>
  <div class="resume-input">
    <div class="row">
      <label>简历内容</label>
      <div class="actions">
        <button type="button" @click="loadSample">加载示例</button>
        <button type="button" @click="fileInput.click()" :disabled="extracting">
          {{ extracting ? '解析中…' : '上传 PDF' }}
        </button>
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,application/pdf"
          hidden
          @change="onPickPdf"
        />
      </div>
    </div>
    <textarea
      :value="modelValue"
      rows="16"
      placeholder="粘贴简历文本，或点击「上传 PDF」自动解析……"
      @input="emit('update:modelValue', $event.target.value)"
    ></textarea>
  </div>
</template>

<style scoped>
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
label {
  font-weight: 600;
}
.actions {
  display: flex;
  gap: 8px;
}
.actions button {
  padding: 6px 12px;
  font-size: 13px;
}
textarea {
  resize: vertical;
  min-height: 320px;
}
</style>
