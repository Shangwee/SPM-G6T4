import './assets/main.css'
import router from './router'
import { createApp } from 'vue'
import App from './App.vue'
import 'bootstrap'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.min.css'


createApp(App)
    .use(router)
    .mount('#app')


