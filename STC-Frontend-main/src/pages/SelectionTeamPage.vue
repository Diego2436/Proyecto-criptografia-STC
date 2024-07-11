<template>
  <v-container class="team_container">
    <div class="team_text">Tus Equipos</div>
    <div class="team_cards">
      <CardTeam v-for="(team, index) in teams" :key="index"
                :team-desc="team.team_desc"
                :team-name="team.team_name"
                @click="redirectTeam(team.team_desc, team.team_name)">
      </CardTeam>
    </div>
    <div class="team-container__buttons">
      <v-btn @click="createTeam" color="primary">Crear Equipo</v-btn>
      <v-btn @click="closeSesion" color="red">Cerrar Sesión</v-btn>
    </div>
  </v-container>
</template>

<script>
import CardTeam from "@/components/CardTeam.vue";
import localforage from "localforage";
import axios from "axios";

export default {
  name: "SelectionTeamPage",
  components: { CardTeam },

  data() {
    return {
      teams: [],
    };
  },
  props: ['user'],
  async mounted() {
    const response = await this.getTeams();
    this.teams = response.data;
  },

  methods: {
    createTeam() {
      this.$router.push({ name: 'crear-equipo' });
    },
    async closeSesion() {
      await localforage.removeItem('authToken');
      this.$router.push({name: 'iniciar-sesion'});
    },
    redirectTeam(teamDesc, teamName) {
      this.$router.push({ name: 'team', params: { teamName: teamName, user: this.user } });
    },
    async getTeams() {

      const config = {
        headers: {
          Authorization: `Bearer ${await localforage.getItem('authToken')}`,
        },
      };

      return await axios.get('http://localhost:5000/equipos/listar', config);
    },
  }
}
</script>

<style scoped lang="scss">
@import "@/styles/mixins";

.team_container {
  text-align: center;
  @include laptop {
    max-width: 50%;
    margin: auto;
  }
}

.team_text {
  font-size: 2em;
  padding-bottom: 1em;
}

.team_cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 2em;

  @include laptop {
    grid-template-columns: repeat(3, 1fr);
    gap: 5em;
  }
}

.team-container__buttons {
  display: flex;
  justify-content: center;
  flex-direction: column;
  gap: 1.5em;
  padding-top: 2em;

  @include laptop {
    gap: 3em;
    flex-direction: row;
    padding-top: 5em;
  }
}
</style>
