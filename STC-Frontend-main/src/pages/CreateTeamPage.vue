<template>
  <v-container class="create-team-container">
    <v-form @submit.prevent="createTeam">
      <div class="create-team_text">Crear Nuevo Equipo</div>
      <v-text-field v-model="name" label="Nombre del equipo"></v-text-field>
      <v-text-field v-model="description" label="Description del equipo"></v-text-field>
      <v-text-field v-model="password" label="Contraseña del equipo" type="password"></v-text-field>

      <v-alert v-show="isAlertVisible" :type="messageAlertType" dismissible>{{ messageAlertText }}</v-alert>

      <div class="create-team-container__buttons">
        <v-btn @click="createTeam" color="primary">Crear</v-btn>
        <v-btn @click="cancel" color="red">Cancelar</v-btn>
      </div>
    </v-form>
  </v-container>
</template>

<script>
import axios from "axios";
import localforage from "localforage";

export default {
  data() {
    return {
      name: '',
      description: '',
      password: '',
      isAlertVisible: false,
      messageAlertText: "",
      messageAlertType: "error",
    };
  },
  props: ['user'],
  methods: {
    async createTeam() {
      try {
        const response = await this.crateTeamPost();
        console.log('Equipo creado:', response.data);
        this.$router.push({name: 'seleccionar-equipo'});
      } catch (error) {
        if (error.response.status === 400) {
          this.messageAlertType = "warning";
          this.messageAlertText = error.response.data.error;
        }
        else {
          console.log(error.response.status)
          this.messageAlertType = "error";
          this.messageAlertText = "Ocurrió un error inesperado. Por favor, inténtelo de nuevo.";
        }
      } finally {
        this.isAlertVisible = true;
      }
    },
    cancel() {
      this.$router.push({ name: 'seleccionar-equipo', params: { user: this.user }});
    },
    async crateTeamPost() {
      const data = {
        team_name: this.name,
        team_desc: this.description,
        team_pw: this.password,
        members: [],
        has_key: false,
      };

      const config = {
        headers: {
          Authorization: `Bearer ${await localforage.getItem('authToken')}`,
        },
      };

      return await axios.post('http://localhost:5000/equipos/crear', data, config);

    },
  }
};
</script>

<style scoped lang="scss">
@import "@/styles/mixins";


.create-team-container {
  @include laptop {
    max-width: 50%;
    margin: auto;
  }
}

.create-team-container__buttons {
  display: flex;
  justify-content: center;
  flex-direction: column;
  gap: 1.5em;
  padding-top: 2em;

  @include laptop {
    gap: 3em;
    flex-direction: row;
  }
}

.create-team_text{
  text-align: center;
  font-size: 2em;
  padding-bottom: 1em;
}
</style>
