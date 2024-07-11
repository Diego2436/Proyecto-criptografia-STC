<template>
  <v-app>
    <v-main>
      <TitleBar></TitleBar>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>

import TitleBar from "@/components/TitleBar.vue";
</script>
