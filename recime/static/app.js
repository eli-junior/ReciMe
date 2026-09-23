"use strict";

const labels = {queued: "Na fila", processing: "Preparando receita", ready: "Pronta para ajustar", failed: "Precisa de atenção", confirmed: "Na biblioteca", discarded: "Descartada"};
let dirty = false;
let saving = false;

async function api(path, method = "GET", body) {
  let response;
  try {
    response = await fetch(path, {method, headers: {"Content-Type": "application/json"},
      body: body === undefined ? undefined : JSON.stringify(body), signal: AbortSignal.timeout(15000)});
  } catch {
    throw new Error("Não foi possível falar com o ReciMe. Confira se o serviço está aberto e tente novamente. Seu texto continua nesta tela.");
  }
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === "string" ? data.detail : "Confira os campos e tente novamente.");
  return data;
}

function message(id, text, error = false) {
  const target = document.getElementById(id);
  if (!target) return;
  target.textContent = text;
  target.classList.toggle("error", error);
}

function element(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function useExample() {
  const input = document.getElementById("url");
  input.value = document.getElementById("use-example").dataset.url;
  input.focus();
}
document.getElementById("use-example")?.addEventListener("click", useExample);
document.getElementById("empty-example")?.addEventListener("click", useExample);

const importForm = document.getElementById("import-form");
importForm?.addEventListener("submit", async event => {
  event.preventDefault();
  const button = importForm.querySelector("button[type=submit]");
  button.disabled = true;
  message("import-message", "Guardando o link…");
  try {
    const data = await api("/api/imports", "POST", {url: document.getElementById("url").value,
      demo_scenario: document.getElementById("demo-scenario").value});
    message("import-message", data.state === "confirmed" ? "Essa receita já está na biblioteca." : `Link guardado. ${labels[data.state]}.`);
    await updateInbox();
  } catch (error) { message("import-message", error.message, true); }
  finally { button.disabled = false; }
});

let inboxSnapshot = null;
async function updateInbox() {
  const list = document.getElementById("inbox-items");
  if (!list) return;
  try {
    const items = await api("/api/imports");
    message("poll-message", "");
    document.getElementById("ready-count").textContent = items.filter(item => item.state === "ready").length;
    const snapshot = JSON.stringify(items.map(item => [item.id, item.version]));
    if (snapshot === inboxSnapshot) return;
    inboxSnapshot = snapshot;
    // Keep the server-rendered empty state, including its keyboard-accessible example button.
    if (!items.length && list.querySelector(".empty-state")) return;
    const focusedHref = list.contains(document.activeElement) ? document.activeElement.getAttribute("href") : null;
    list.replaceChildren();
    if (!items.length) {
      const empty = element("div", "empty-state");
      empty.append(element("div", "empty-icon", "✳"), element("h3", "", "Tudo em dia por aqui."), element("p", "", "Suas próximas receitas vão aparecer nesta caixa."));
      list.append(empty);
    }
    for (const item of items) {
      const card = element("article", "import-card");
      const glyph = element("div", "recipe-glyph", item.state === "ready" ? "✳" : "↗");
      glyph.setAttribute("aria-hidden", "true");
      const copy = element("div", "card-copy");
      copy.append(element("span", `status ${item.state}`, labels[item.state]),
        element("h3", "", item.draft?.title || "Receita do Instagram"),
        element("p", "", item.error || (item.state === "ready" ? "Confira os ingredientes e dê seu toque final." : "Você pode sair desta página e voltar depois.")),
        element("span", "source-code", `Instagram · ${item.code}`));
      const link = element("a", "card-link", item.state === "ready" ? "Ajustar receita ↗" : "Ver detalhes ↗");
      link.href = `/imports/${item.id}`;
      card.append(glyph, copy, link);
      list.append(card);
      if (focusedHref === link.getAttribute("href")) link.focus();
    }
  } catch (error) { message("poll-message", error.message, true); }
}

const detailPoll = document.querySelector('[data-poll="detail"]');
async function poll() {
  if (!document.hidden) {
    if (importForm) await updateInbox();
    if (detailPoll) {
      try {
        const data = await api(`/api/imports/${detailPoll.dataset.id}`);
        if (data.state !== detailPoll.dataset.state) location.reload();
        message("poll-message", "");
      } catch (error) { message("poll-message", error.message, true); }
    }
  }
  if (importForm || detailPoll) setTimeout(poll, 2500);
}
poll();

const reviewForm = document.getElementById("review-form");
reviewForm?.addEventListener("input", () => {
  dirty = true;
  message("review-message", "Alterações ainda não guardadas.");
});
window.addEventListener("beforeunload", event => {
  if (dirty) { event.preventDefault(); event.returnValue = ""; }
});

function numberSteps() {
  document.querySelectorAll("#steps .step-row").forEach((row, index) => {
    row.querySelector(".step-number").textContent = index + 1;
    row.querySelector(".sr-only").textContent = `Etapa ${index + 1}`;
  });
}

reviewForm?.addEventListener("click", event => {
  const remove = event.target.closest(".remove-button");
  if (remove) {
    const container = remove.closest(".edit-row").parentElement;
    remove.closest(".edit-row").remove();
    dirty = true;
    numberSteps();
    reviewForm.querySelector(`[data-add="${container.id}"]`).focus();
    message("review-message", "Alterações ainda não guardadas.");
  }
  const add = event.target.closest("[data-add]");
  if (!add) return;
  const kind = add.dataset.add;
  const container = document.getElementById(kind);
  if (container.children.length >= 100) { message("review-message", "O limite é de 100 itens por lista.", true); return; }
  const row = element("div", `${kind === "ingredients" ? "ingredient-row" : "step-row"} edit-row`);
  if (kind === "steps") {
    const number = element("span", "step-number");
    number.setAttribute("aria-hidden", "true");
    row.append(number);
  }
  const fields = kind === "ingredients" ? [["name", "Ingrediente", 500], ["quantity_text", "Quantidade", 200]] : [["instruction", "Etapa", 4000]];
  for (const [field, labelText, limit] of fields) {
    const label = element("label");
    const input = element(kind === "ingredients" ? "input" : "textarea");
    input.dataset.field = field;
    input.maxLength = limit;
    input.placeholder = "não informado";
    if (kind === "steps") input.rows = 3;
    label.append(element("span", "sr-only", labelText), input);
    row.append(label);
  }
  const button = element("button", "remove-button", "×");
  button.type = "button";
  button.setAttribute("aria-label", kind === "ingredients" ? "Remover ingrediente" : "Remover etapa");
  row.append(button);
  container.append(row);
  numberSteps();
  row.querySelector("input, textarea").focus();
  dirty = true;
});

function readRows(kind) {
  return Array.from(document.querySelectorAll(`#${kind} .edit-row`), row => {
    const value = {id: row.dataset.itemId === undefined ? null : Number(row.dataset.itemId)};
    row.querySelectorAll("[data-field]").forEach(input => { value[input.dataset.field] = input.value.trim() || null; });
    return value;
  });
}

async function saveReview(confirm) {
  if (saving) return;
  saving = true;
  const buttons = Array.from(reviewForm.querySelectorAll("button"));
  buttons.forEach(button => { button.disabled = true; });
  // Freeze inputs during the request so a late response cannot mark new edits as saved.
  const fields = Array.from(reviewForm.querySelectorAll("input, textarea"));
  fields.forEach(field => { field.readOnly = true; });
  message("review-message", "Guardando suas alterações…");
  try {
    const result = await api(`/api/imports/${reviewForm.dataset.id}/draft`, "PATCH", {
      version: Number(reviewForm.dataset.version), title: document.getElementById("title").value.trim() || null,
      ingredients: readRows("ingredients"), steps: readRows("steps")});
    reviewForm.dataset.version = result.version;
    for (const kind of ["ingredients", "steps"]) {
      document.querySelectorAll(`#${kind} .edit-row`).forEach((row, index) => { row.dataset.itemId = result.draft[kind][index].id; });
    }
    dirty = false;
    if (confirm) {
      const recipe = await api(`/api/imports/${reviewForm.dataset.id}/confirm`, "POST", {version: result.version});
      location.assign(`/recipes/${recipe.id}`);
    } else { message("review-message", "Rascunho guardado. Ainda não está na biblioteca."); }
  } catch (error) { message("review-message", error.message, true); }
  finally {
    saving = false;
    buttons.forEach(button => { button.disabled = false; });
    fields.forEach(field => { field.readOnly = false; });
  }
}
reviewForm?.addEventListener("submit", event => { event.preventDefault(); saveReview(true); });
document.getElementById("save-draft")?.addEventListener("click", () => saveReview(false));

document.querySelectorAll("[data-action]").forEach(button => {
  button.addEventListener("click", async () => {
    button.disabled = true;
    const messageId = reviewForm ? "review-message" : "action-message";
    try {
      await api(`/api/imports/${button.dataset.id}/${button.dataset.action}`, "POST");
      dirty = false;
      location.assign(button.dataset.action === "discard" ? "/" : `/imports/${button.dataset.id}`);
    } catch (error) { message(messageId, error.message, true); button.disabled = false; }
  });
});
