import { createRouter, createWebHistory } from "vue-router";
import Home from '@/components/HomePage.vue'
import Login  from "@/components/Login.vue";
import OwnSchedule from "@/components/OwnSchedule.vue";
import TeamSchedule from "@/components/TeamSchedule.vue";
import Arrangements from "@/components/Arrangements.vue";
import Requests from "@/components/Requests.vue";
import Notifications from "@/components/Notifications.vue";


const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        path: '/teamschedule',
        name: 'TeamSchedule',
        component: TeamSchedule
    },
    {
        path: '/ownschedule',
        name: 'OwnSchedule',
        component: OwnSchedule
    },
    {
        path: '/requests',
        name: 'Requests',
        component: Requests
    },

    {
        path: '/arrangements', 
        name: 'Arrangements',
        component: Arrangements,
    },
    {
        path: '/notifications',
        name: 'Notifications',
        component: Notifications,
    },


]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router;