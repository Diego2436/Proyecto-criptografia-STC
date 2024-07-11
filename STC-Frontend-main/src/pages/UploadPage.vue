<template>
  <v-container class="create-key-container">
    <v-form @submit.prevent="validateFragment">
      <div class="create-key_text">Subir Archivo</div>

      <div class="create-key-container__buttons">

        <div class="text-center">
          <v-menu open-on-hover >
            <template v-slot:activator="{ props }">
              <v-btn color="secondary" v-bind="props"> Seleccione un archivo </v-btn>
            </template>

            <v-list>
              <v-list-item v-for="(item, index) in items" :key="index" >
                <v-list-item-title>{{  itemSelected = item.title }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
          <div>{{ itemSelected }}</div>
        </div>

        <v-btn color="primary">Subir Archivo</v-btn>
        <v-btn @click="cancel" color="red">Cancelar</v-btn>
      </div>
    </v-form>
  </v-container>
</template>

<script>
export default {
  name: "UploadPage",
  data() {
    return {
      user: '',
      generateKeyButtonColor: 'grey',
      generateKeyCursorStyle: 'default',
      validateBoxClass: 'download-validate_box',
      items: [
        { title: 'Archivo 1' },
        { title: 'Archivo 2' },
        { title: 'Archivo 3' },
        { title: 'Archivo 4' },
      ],
      itemSelected: "Seleccione un Archivo"
    };
  },
  methods: {
    validateFragment() {
      this.isAddUserVisible = true;
      this.generateKeyButtonColor = 'secondary';
      this.generateKeyCursorStyle = 'pointer';
      this.validateBoxClass = 'download-validate_box_correct';
    },
    cancel() {
      this.$router.push({name: 'descargar'});
    }
  }
}

</script>


<style scoped lang="scss">
@import "@/styles/mixins";


.create-key-container {
  @include laptop {
    max-width: 50%;
    margin: auto;
  }
}

.create-key-container__buttons {
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

.create-key_text {
  text-align: center;
  font-size: 2em;
  padding-bottom: 1em;
}

.download-validate_container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  justify-content: center;
  align-items: center;
  gap: 0.5em;
}

.download-validate_box {
  padding: 1em;
  background-color: red;
}

.download-validate_box_correct {
  padding: 1em;
  background-color: greenyellow;
}

.download-keys_buttons {
  padding-top: 1em;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
}
</style>

