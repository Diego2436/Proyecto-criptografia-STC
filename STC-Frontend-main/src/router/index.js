import { createRouter, createWebHistory } from 'vue-router'
import localforage from 'localforage';

import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegistroPage.vue'
import SelectionTeamPage from '@/pages/SelectionTeamPage.vue'
import CreateTeamPage from "@/pages/CreateTeamPage.vue";
import CreateMasterKeyPage from "@/pages/CreateMasterKeyPage.vue";
import DownloadPage from "@/pages/DownloadPage.vue";
import UploadPage from "@/pages/UploadPage.vue";

async function isAuthenticated() {
  const authToken = await localforage.getItem('authToken');
  return !!authToken; // Devuelve true si authToken no es null o undefined
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/iniciar-sesion' },
    {
      path: '/iniciar-sesion',
      name: 'iniciar-sesion',
      component: LoginPage
    },
    {
      path: '/registro',
      name: 'registro',
      component: RegisterPage
    },
    {
      path: '/seleccionar-equipo/:user',
      name: 'seleccionar-equipo',
      props: true,
      component: SelectionTeamPage,
      meta: { requiresAuth: true }
    },
    {
      path: '/crear-equipo/:user',
      name: 'crear-equipo',
      component: CreateTeamPage,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/team/:teamName/:user',
      name: 'team',
      component: CreateMasterKeyPage,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/descargar/:teamName/:user',
      name: 'descargar',
      component: DownloadPage,
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/subir',
      name: 'subir',
      component: UploadPage,
      meta: { requiresAuth: true }
    },
  ]
})

router.beforeEach(async (to, from, next) => {
  // Verifica si la ruta requiere autenticación
  if (to.meta.requiresAuth) {
    const authenticated = await isAuthenticated();
    if (authenticated) {
      next(); // Permite navegar a la ruta
    } else {
      next({ name: 'iniciar-sesion' }); // Redirige a la página de inicio de sesión si no está autenticado
    }
  } else {
    next(); // Si la ruta no requiere autenticación, permite navegar a la ruta
  }
});

export default router
