<template>
  <div class="card-team_container">
    <div>"{{ teamName }}"</div>
    <div>{{ teamDesc }}</div>
  </div>
</template>

<script>
export default {
  name: "CardTeam",
  props: {
    teamDesc: {
      type: String,
      default: "",
      required: true
    },
    teamName: {
      type: String,
      default: "",
      required: true
    },
  }
}
</script>

<style scoped lang="scss">
.card-team_container {
  cursor: pointer;
  padding: 15%;
  color: white;
  background-color: orangered;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>
