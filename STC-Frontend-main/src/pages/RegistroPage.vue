<template>
  <v-container class="register-container">
    <v-form>
      <div class="register_text">Registrarse</div>
      <v-text-field v-model="username" label="Nombre de usuario"></v-text-field>
      <v-text-field v-model="email" label="Correo" type="email"></v-text-field>
      <v-text-field v-model="password" label="Contraseña" type="password"></v-text-field>

      <v-alert v-show="isAlertVisible" :type="messageAlertType" dismissible>
        {{ messageAlertText }} <v-btn @click="redirectToLogin" v-show="isBtnLoginVisible"> Iniciar Sesion </v-btn>
      </v-alert>

      <div class="register-container__buttons">
        <v-btn @click="register" color="primary" :disabled="isBtnDisabled">Registrarse</v-btn>
        <v-btn @click="redirectToLogin" color="red" :disabled="isBtnDisabled">Cancelar</v-btn>
      </div>
    </v-form>
  </v-container>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      username: '',
      email: '',
      password: '',
      isAlertVisible: false,
      isBtnDisabled: false,
      isBtnLoginVisible: false,
      messageAlertText: "",
      messageAlertType: "success",
    };
  },
  methods: {
    async register() {
      try {
        const responseRegister = await this.registerPost();
        this.messageAlertType = "success";
        this.messageAlertText = responseRegister.data.message;
        this.isBtnLoginVisible = true;
        this.isBtnDisabled = true;
      } catch (error) {
        if (error.response.status === 400) {
          this.messageAlertType = "warning";
          this.messageAlertText = error.response.data.error;
        } else {
          this.messageAlertType = "error";
          this.messageAlertText = "Ocurrió un error inesperado. Por favor, inténtelo de nuevo.";
        }
      } finally {
        this.isAlertVisible = true;
      }
    },
    redirectToLogin() {
      this.$router.push({name: 'iniciar-sesion'});
    },
    async registerPost() {
      const data = {
        username: this.username,
        email: this.email,
        password: this.password
      };
      return await axios.post('http://localhost:5000/usuarios/registrar', data);
    },
  }
};
</script>

<style scoped lang="scss">
@import "@/styles/mixins";

.register-container {
  @include laptop {
    max-width: 50%;
    margin: auto;
  }
}

.register-container__buttons {
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

.register_text {
  text-align: center;
  font-size: 2em;
  padding-bottom: 1em;
}
</style>
