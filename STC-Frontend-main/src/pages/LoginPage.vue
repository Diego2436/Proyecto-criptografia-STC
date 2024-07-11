<template>
  <v-container class="login-container">
    <v-form>
      <div class="login_text">Iniciar Sesión</div>
      <v-text-field v-model="username" label="Nombre de usuario"></v-text-field>
      <v-text-field v-model="password" label="Contraseña" type="password"></v-text-field>

      <v-alert v-show="isAlertVisible" :type="messageAlertType" dismissible>{{ messageAlertText }}</v-alert>

      <div class="login-container__buttons">
        <v-btn @click="login" color="primary">Iniciar Sesión</v-btn>
        <v-btn @click="register" color="secondary">Registrarse</v-btn>
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
      username: '',
      password: '',
      isAlertVisible: false,
      isBtnLoginVisible: false,
      messageAlertText: "",
      messageAlertType: "error",
    };
  },
  methods: {
    async login() {
      try {
        const responseLogin = await this.loginPost();
        await localforage.setItem('authToken', responseLogin.data.token);
        this.$router.push({ name: 'seleccionar-equipo', params: { user: this.username } });
      } catch (error) {
        if (error.response.status === 400) {
          this.messageAlertType = "warning";
          this.messageAlertText = error.response.data.error;
        }
        else if (error.response.status === 401) {
          this.messageAlertType = "error";
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
    register() {
      this.$router.push({ name: 'registro' });
    },
    async loginPost() {
      const data = {
        username: this.username,
        password: this.password
      };
      return await axios.post('http://localhost:5000/usuarios/login', data);
    },
  }
};
</script>

<style scoped lang="scss">
@import "@/styles/mixins";


.login-container {
  @include laptop {
    max-width: 50%;
    margin: auto;
  }
}

.login-container__buttons {
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

.login_text{
  text-align: center;
  font-size: 2em;
  padding-bottom: 1em;
}
</style>
