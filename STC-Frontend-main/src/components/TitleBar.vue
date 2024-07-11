<template>
  <div class="title-bar__container">
    <v-app-bar app color="primary">
      <div class="title-bar__content">
        <div class="title-bar__item">Nombre Empresa</div>
      </div>
    </v-app-bar>
  </div>
</template>

<script setup>

</script>

<style scoped lang="scss">

.title-bar__container {
  margin-bottom: 2em;
}

.title-bar__content {
  display: flex;
  justify-content: center;
  width: 100%;
}

.title-bar__item {
  margin: 0 10px;
}
</style>
