<script setup>
import WelcomeItem from "./WelcomeItem.vue";
import DocumentationIcon from "./icons/IconDocumentation.vue";
import ToolingIcon from "./icons/IconTooling.vue";
import CommunityIcon from "./icons/IconCommunity.vue";
import NavBar from "./NavBar.vue";
</script>

<template>
  <NavBar></NavBar>
  <div id="app" class="container border rounded-3 bg-white bg-opacity-75 p-5">
    <div class="row">
      <div class="col">
        <img
          alt="Vue logo"
          class="logo"
          src="../assets/home.png"
          width="400px"
          height="400px"
        />
      </div>
      <div class="col">
        <div>
          <WelcomeItem>
            <template #icon>
              <DocumentationIcon />
            </template>
            <div>
              <h3>View Own Schedule</h3>
              <p>
                shit
              </p>
            </div>
          </WelcomeItem>

          <WelcomeItem>
            <template #icon>
              <ToolingIcon />
            </template>
            <div>
              <h3>View Team Schedule</h3>
              <p>
                shit2
              </p>
              <br />
            </div>
          </WelcomeItem>

          <WelcomeItem>
            <template #icon>
              <CommunityIcon />
            </template>
            <div>
              <div><h3>Arrangements</h3></div>
              <p>
                shit3
              </p>
            </div>
          </WelcomeItem>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  margin-top: 150px;
}
header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
  #app {
    grid-template-columns: 1fr 1fr;
    
  }
}
.img {
  background-image: url("../assets/94999.png");
  overflow: hidden;
  width: 100%;
  height: 100%;
  background-size: contain;
}
</style>
