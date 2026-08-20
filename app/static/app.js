let token = sessionStorage.getItem("token") || "";
let adminKey = sessionStorage.getItem("adminKey") || "";
let currentUser = null;
let adminUsersCache = [];

async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;
  if (options.admin) headers["X-Admin-Key"] = adminKey;
  if (options.json) headers["Content-Type"] = "application/json";
  const response = await fetch(path, { ...options, headers, body: options.json ? JSON.stringify(options.json) : options.body });
  const text = await response.text();
  const data = text ? (() => { try { return JSON.parse(text); } catch { return text; } })() : null;
  if (!response.ok) throw new Error(data?.detail || `Erro HTTP ${response.status}`);
  return data;
}

function notify(message, error = false) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.className = `toast${error ? " error" : ""}`;
  setTimeout(() => toast.classList.add("hidden"), 3500);
}

function showAccessTab(tab) {
  document.getElementById("loginForm").classList.toggle("hidden", tab !== "login");
  document.getElementById("registerForm").classList.toggle("hidden", tab !== "register");
  document.getElementById("loginTab").classList.toggle("active", tab === "login");
  document.getElementById("registerTab").classList.toggle("active", tab === "register");
}

function toggleAdminKey() {
  document.getElementById("adminKeyLabel").classList.toggle("hidden", !document.getElementById("adminMode").checked);
}

async function registerUser(event) {
  event.preventDefault();
  const form = new FormData(event.target);
  try {
    await api("/usuarios", { method: "POST", json: Object.fromEntries(form) });
    event.target.reset();
    showAccessTab("login");
    notify("Conta criada. Agora faça seu login.");
  } catch (error) { notify(error.message, true); }
}

async function login(event) {
  event.preventDefault();
  const form = new FormData(event.target);
  const body = new URLSearchParams({ username: form.get("username"), password: form.get("password") });
  try {
    const result = await api("/usuarios/login", { method: "POST", body, headers: { "Content-Type": "application/x-www-form-urlencoded" } });
    token = result.access_token;
    sessionStorage.setItem("token", token);
    currentUser = await api("/usuarios/me");
    const adminMode = document.getElementById("adminMode").checked;
    if (adminMode) {
      adminKey = document.getElementById("adminKey").value;
      sessionStorage.setItem("adminKey", adminKey);
      await api("/admin/usuarios", { admin: true });
    } else {
      adminKey = "";
      sessionStorage.removeItem("adminKey");
    }
    openApplication(adminMode);
  } catch (error) { token = ""; sessionStorage.clear(); notify(error.message, true); }
}

function openApplication(adminMode) {
  document.getElementById("accessView").classList.add("hidden");
  document.getElementById("sessionBox").classList.remove("hidden");
  document.getElementById("sessionName").textContent = currentUser?.nome || "Sessão ativa";
  document.getElementById("userView").classList.toggle("hidden", adminMode);
  document.getElementById("adminView").classList.toggle("hidden", !adminMode);
  if (adminMode) loadAdminUsers(); else loadUserHome();
}

function logout() {
  token = ""; adminKey = ""; currentUser = null; sessionStorage.clear();
  document.getElementById("userView").classList.add("hidden");
  document.getElementById("adminView").classList.add("hidden");
  document.getElementById("sessionBox").classList.add("hidden");
  document.getElementById("accessView").classList.remove("hidden");
}

function showPanel(id) {
  document.querySelectorAll("#userView .panel").forEach(element => element.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}

function showAdminPanel(id) {
  document.querySelectorAll(".admin-panel").forEach(element => element.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
}

async function loadUserHome() {
  showPanel("userHome");
  try {
    const [saldo, bets] = await Promise.all([api("/usuarios/me/saldo"), api("/apostas/minhas/ativas")]);
    document.getElementById("balance").textContent = `${saldo.saldo} pts`;
    document.getElementById("activeBets").innerHTML = bets.length ? bets.map(betCard).join("") : "<p class='meta'>Nenhuma aposta ativa.</p>";
  } catch (error) { notify(error.message, true); }
}

function betCard(bet) {
  return `<article class="card bet"><div class="bet-heading"><strong>Aposta #${bet.id}</strong><span class="badge">${bet.status}</span></div><h3>Partida #${bet.partida_id} · ${bet.gols_casa} × ${bet.gols_visitante}</h3><p class="meta">${bet.valor_total} pts · ODD ${bet.odd_registrada} · multiplicador x${bet.multiplicador}</p>${bet.status === "PENDING" ? `<button onclick="multiplyBet(${bet.id})">Multiplicar</button>` : ""}</article>`;
}

async function loadMatches(status = "SCHEDULED") {
  try {
    const matches = await api(`/partidas?status=${status}`);
    const finished = status === "FINISHED";
    document.getElementById("matchesTitle").textContent = finished ? "Partidas encerradas" : "Partidas agendadas";
    document.getElementById("matches").innerHTML = matches.length ? matches.map(match => {
      const details = finished
        ? `<p class="match-score">${match.gols_casa} × ${match.gols_visitante}</p><p class="meta">Resultado final · ${match.fase}</p>`
        : `<p class="meta">ODDs ${match.odd_casa} / ${match.odd_visitante}</p><button onclick="placeBet(${match.id}, '${match.time_casa}', '${match.time_visitante}')">Apostar</button>`;
      return `<article class="card match"><span class="badge">${match.status}</span><h3>${match.time_casa} × ${match.time_visitante}</h3>${details}</article>`;
    }).join("") : `<p>Nenhuma partida ${finished ? "encerrada" : "agendada"}.</p>`;
  } catch (error) { notify(error.message, true); }
}

async function placeBet(matchId, home, away) {
  const homeGoals = prompt(`Gols de ${home}:`); if (homeGoals === null) return;
  const awayGoals = prompt(`Gols de ${away}:`); if (awayGoals === null) return;
  const value = prompt("Quantos pontos deseja apostar?"); if (value === null) return;
  try {
    await api("/apostas", { method: "POST", json: { partida_id: matchId, gols_casa: Number(homeGoals), gols_visitante: Number(awayGoals), valor_apostado: value } });
    notify("Aposta registrada com sucesso."); loadMatches();
  } catch (error) { notify(error.message, true); }
}

async function loadBets() {
  try { const bets = await api("/apostas/minhas"); document.getElementById("bets").innerHTML = bets.length ? bets.map(betCard).join("") : "<p>Nenhuma aposta registrada.</p>"; }
  catch (error) { notify(error.message, true); }
}

async function multiplyBet(id) {
  const factor = prompt("Multiplicador (2, 3, 4 ou 5):", "2"); if (!factor) return;
  try { await api(`/apostas/${id}/multiplicar`, { method: "PATCH", json: { multiplicador: Number(factor) } }); notify("Aposta multiplicada."); loadBets(); }
  catch (error) { notify(error.message, true); }
}

async function loadRanking() {
  try {
    const ranking = await api("/usuarios/ranking");
    document.getElementById("ranking").innerHTML = table(["Posição", "Nome", "Saldo", "Ativo"], ranking.map(item => [item.posicao, item.nome, item.saldo, item.ativo ? "Sim" : "Não"]));
  } catch (error) { notify(error.message, true); }
}

async function changePassword(event) {
  event.preventDefault(); const data = Object.fromEntries(new FormData(event.target));
  try { await api("/usuarios/me/senha", { method: "PATCH", json: data }); event.target.reset(); notify("Senha alterada."); }
  catch (error) { notify(error.message, true); }
}

async function deactivateAccount() {
  if (!confirm("Deseja realmente inativar sua conta?")) return;
  try { await api("/usuarios/me/inativar", { method: "PATCH" }); notify("Conta inativada."); setTimeout(logout, 1000); }
  catch (error) { notify(error.message, true); }
}

function table(headers, rows) {
  return `<div class="table-wrap"><table><thead><tr>${headers.map(h => `<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.map(row => `<tr>${row.map(value => `<td>${value}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, character => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[character]);
}

async function loadAdminUsers() {
  try {
    adminUsersCache = await api("/admin/usuarios", { admin: true });
    sortAdminUsers("id");
  } catch (error) { notify(error.message, true); }
}

async function loadAdminMatchesView(status = "SCHEDULED") {
  try {
    const matches = await api(`/partidas?status=${status}`);
    const finished = status === "FINISHED";
    document.getElementById("adminMatchesTitle").textContent = finished ? "Partidas encerradas" : "Partidas agendadas";
    document.getElementById("adminMatchesList").innerHTML = matches.length ? matches.map(match => {
      const date = new Date(match.inicio_em).toLocaleString("pt-BR");
      const details = finished
        ? `<p class="match-score">${match.gols_casa} × ${match.gols_visitante}</p><p class="meta">Resultado final</p>`
        : `<p class="meta">ODD casa: ${match.odd_casa} · ODD visitante: ${match.odd_visitante}</p>`;
      return `<article class="card match"><div class="bet-heading"><strong>Partida #${match.id}</strong><span class="badge">${match.status}</span></div><h3>${escapeHtml(match.time_casa)} × ${escapeHtml(match.time_visitante)}</h3>${details}<p class="meta">${escapeHtml(match.fase)} · ${date}</p></article>`;
    }).join("") : `<p>Nenhuma partida ${finished ? "encerrada" : "agendada"}.</p>`;
  } catch (error) { notify(error.message, true); }
}

async function syncMatches() {
  if (!confirm("Deseja importar ou atualizar as partidas usando a API externa?")) return;
  try {
    const result = await api("/partidas/sincronizar", { method: "POST", admin: true });
    notify(`Sincronização concluída: ${result.partidas_criadas} criadas e ${result.partidas_atualizadas} atualizadas.`);
    loadAdminMatchesView("SCHEDULED");
    loadAdminMatches();
  } catch (error) { notify(error.message, true); }
}

function sortAdminUsers(order) {
  const users = [...adminUsersCache];
  if (order === "saldo") users.sort((first, second) => Number(second.saldo) - Number(first.saldo) || first.id - second.id);
  else if (order === "nome") users.sort((first, second) => first.nome.localeCompare(second.nome, "pt-BR"));
  else users.sort((first, second) => first.id - second.id);
  document.getElementById("users").innerHTML = table(["ID", "Nome", "Login", "Saldo", "Ativo"], users.map(user => [user.id, `<button class="link-button" onclick="viewAdminUser(${user.id})">${escapeHtml(user.nome)}</button>`, escapeHtml(user.login), user.saldo, user.ativo ? "Sim" : "Não"]));
}

async function viewAdminUser(id) {
  try {
    const user = await api(`/admin/usuarios/${id}`, { admin: true });
    const detail = document.getElementById("adminUserDetail");
    detail.innerHTML = `<div class="section-title"><h2>Dados do usuário #${user.id}</h2><button class="ghost" onclick="this.closest('.user-detail').classList.add('hidden')">Fechar</button></div><dl><dt>Nome</dt><dd>${escapeHtml(user.nome)}</dd><dt>Login</dt><dd>${escapeHtml(user.login)}</dd><dt>E-mail</dt><dd>${escapeHtml(user.email)}</dd><dt>CPF</dt><dd>${escapeHtml(user.cpf)}</dd><dt>Nascimento</dt><dd>${escapeHtml(user.data_nascimento)}</dd><dt>Saldo</dt><dd>${user.saldo} pontos</dd><dt>Situação</dt><dd>${user.ativo ? "Ativo" : "Inativo"}</dd><dt>Cadastrado em</dt><dd>${new Date(user.criado_em).toLocaleString("pt-BR")}</dd></dl>`;
    detail.classList.remove("hidden");
  } catch (error) { notify(error.message, true); }
}

async function loadAdminMatches() {
  try {
    const matches = await api("/partidas?status=SCHEDULED");
    const options = matches.map(match => `<option value="${match.id}">#${match.id} — ${match.time_casa} × ${match.time_visitante}</option>`).join("");
    document.querySelectorAll(".admin-match-select").forEach(select => select.innerHTML = options || "<option>Nenhuma partida agendada</option>");
  } catch (error) { notify(error.message, true); }
}

async function createAdminBet(event) {
  event.preventDefault(); const raw = Object.fromEntries(new FormData(event.target));
  const data = { usuario_id: Number(raw.usuario_id), partida_id: Number(raw.partida_id), gols_casa: Number(raw.gols_casa), gols_visitante: Number(raw.gols_visitante), valor_apostado: raw.valor_apostado };
  try { const result = await api("/admin/apostas", { method: "POST", admin: true, json: data }); notify(`Aposta #${result.id} criada.`); event.target.reset(); }
  catch (error) { notify(error.message, true); }
}

async function searchAdmin(event, resource) {
  event.preventDefault(); const id = new FormData(event.target).get("id");
  try { const result = await api(`/admin/${resource}/${id}`, { admin: true }); const output = document.getElementById("adminSearchResult"); output.textContent = JSON.stringify(result, null, 2); output.classList.remove("hidden"); }
  catch (error) { notify(error.message, true); }
}

async function closeMatch(event) {
  event.preventDefault(); const raw = Object.fromEntries(new FormData(event.target));
  if (!confirm(`Confirma o placar ${raw.gols_casa} × ${raw.gols_visitante}? A liquidação não pode ser repetida.`)) return;
  try {
    const result = await api(`/partidas/${raw.partida_id}/resultado`, { method: "PATCH", admin: true, json: { gols_casa: Number(raw.gols_casa), gols_visitante: Number(raw.gols_visitante) } });
    notify(`Partida encerrada: ${result.placar}`);
    event.target.reset();
    loadAdminMatches();
  }
  catch (error) { notify(error.message, true); }
}

if (token) {
  api("/usuarios/me").then(user => { currentUser = user; openApplication(Boolean(adminKey)); }).catch(logout);
}
