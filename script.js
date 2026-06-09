const scoreEl = document.querySelector("#score");
const beansPerClickEl = document.querySelector("#beans-per-click");
const clickButton = document.querySelector("#click-button");
const upgradesEl = document.querySelector("#upgrades");
const screenshotButton = document.querySelector("#screenshot-button");
const downloadLink = document.querySelector("#download-link");
const canvas = document.querySelector("#score-canvas");
const ctx = canvas.getContext("2d");

let score = 0;
let beansPerClick = 1;

const upgrades = [
  {
    name: "Tiny Spoon",
    description: "+1 bean every click.",
    cost: 15,
    gain: 1,
    bought: false,
  },
  {
    name: "Bean Megaphone",
    description: "+5 beans every click. It shouts compliments.",
    cost: 75,
    gain: 5,
    bought: false,
  },
  {
    name: "Pocket Bean Wizard",
    description: "+20 beans every click. Probably licensed.",
    cost: 250,
    gain: 20,
    bought: false,
  },
];

const funnyCaptions = [
  "Certified bean billionaire energy.",
  "This score has been inspected by a confused raccoon.",
  "Screenshot powered by tiny applause noises.",
  "Your bean accountant is sweating.",
  "A perfectly normal amount of beans. Definitely.",
];

function formatBeans(amount) {
  return new Intl.NumberFormat("en-US").format(amount);
}

function updateDisplay() {
  scoreEl.textContent = formatBeans(score);
  beansPerClickEl.textContent = `${formatBeans(beansPerClick)} ${beansPerClick === 1 ? "bean" : "beans"} per click`;

  document.querySelectorAll(".buy-button").forEach((button, index) => {
    button.disabled = upgrades[index].bought || score < upgrades[index].cost;
  });
}

function renderUpgrades() {
  upgradesEl.innerHTML = "";

  upgrades.forEach((upgrade, index) => {
    const card = document.createElement("article");
    card.className = "upgrade-card";
    card.innerHTML = `
      <h3>${upgrade.name}</h3>
      <p>${upgrade.description}</p>
      <button class="buy-button" type="button">
        ${upgrade.bought ? "Bought" : `Buy for ${formatBeans(upgrade.cost)} beans`}
      </button>
    `;

    const button = card.querySelector("button");
    button.addEventListener("click", () => buyUpgrade(index));
    upgradesEl.append(card);
  });

  updateDisplay();
}

function buyUpgrade(index) {
  const upgrade = upgrades[index];

  if (upgrade.bought || score < upgrade.cost) {
    return;
  }

  score -= upgrade.cost;
  beansPerClick += upgrade.gain;
  upgrade.bought = true;
  renderUpgrades();
}

function getRandomCaption() {
  return funnyCaptions[Math.floor(Math.random() * funnyCaptions.length)];
}

function drawFunnyScreenshot() {
  const caption = getRandomCaption();
  const boughtCount = upgrades.filter((upgrade) => upgrade.bought).length;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  gradient.addColorStop(0, "#fff7d6");
  gradient.addColorStop(1, "#ff9f52");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "rgba(255, 255, 255, 0.42)";
  for (let i = 0; i < 16; i += 1) {
    ctx.beginPath();
    ctx.arc(Math.random() * canvas.width, Math.random() * canvas.height, 18 + Math.random() * 48, 0, Math.PI * 2);
    ctx.fill();
  }

  ctx.fillStyle = "#2f261f";
  ctx.font = "900 46px Trebuchet MS, Arial";
  ctx.fillText("Tiny Bean Clicker Receipt", 48, 78);

  ctx.font = "900 104px Trebuchet MS, Arial";
  ctx.fillText(formatBeans(score), 48, 190);

  ctx.font = "800 32px Trebuchet MS, Arial";
  ctx.fillText(`${formatBeans(beansPerClick)} beans per click`, 52, 240);
  ctx.fillText(`${boughtCount} of ${upgrades.length} upgrades owned`, 52, 285);

  ctx.fillStyle = "#d45b1c";
  ctx.font = "900 34px Trebuchet MS, Arial";
  ctx.fillText("🫘", 585, 108);
  ctx.fillText("🫘", 625, 160);
  ctx.fillText("🫘", 560, 220);

  ctx.fillStyle = "#2f261f";
  ctx.font = "700 26px Trebuchet MS, Arial";
  ctx.fillText(caption, 48, 355);

  const imageUrl = canvas.toDataURL("image/png");
  downloadLink.href = imageUrl;
  downloadLink.classList.remove("disabled");
  downloadLink.removeAttribute("aria-disabled");
}

clickButton.addEventListener("click", () => {
  score += beansPerClick;
  updateDisplay();
});

screenshotButton.addEventListener("click", drawFunnyScreenshot);

renderUpgrades();
drawFunnyScreenshot();
