// Filtering, searching, sorting and paging the ticket list.
// Read-only: nothing here changes a ticket. Without JavaScript, every ticket still shows.

(function () {
  // Every 30 seconds, ask the server whether any tickets have arrived since this page
  // was loaded (through the Report a problem form). If so, show a "new tickets" message.
  const queue = document.getElementById("queue");
  const newTickets = document.getElementById("new-tickets");
  if (queue && newTickets) {
    const checkUrl = queue.dataset.checkUrl + "?since=" + encodeURIComponent(queue.dataset.latest);
    setInterval(function () {
      fetch(checkUrl, { headers: { Accept: "application/json" } })
        .then(function (response) { return response.ok ? response.json() : null; })
        .then(function (data) {
          if (!data || data.count < 1) return;
          newTickets.querySelector(".new-count").textContent =
            data.count === 1 ? "1 new ticket has" : data.count + " new tickets have";
          newTickets.hidden = false;
        })
        .catch(function () { /* offline or signed out: try again next time */ });
    }, 30000);
  }

  const list = document.getElementById("ticket-list");
  if (!list) return;

  const PAGE_SIZE = 10;   // how many tickets to show on each page

  const toolbar = document.getElementById("toolbar");
  const showing = document.getElementById("showing");
  const noMatch = document.getElementById("no-match");
  const search = document.getElementById("search");
  const sort = document.getElementById("sort");
  const reviewFilter = document.getElementById("review-filter");
  const priorityButtons = Array.from(document.querySelectorAll(".filter[data-priority]"));
  const pager = document.getElementById("pager");
  const prevButton = document.getElementById("prev-page");
  const nextButton = document.getElementById("next-page");
  const pageLabel = document.getElementById("page-label");
  const tickets = Array.from(list.children);

  // What the person has chosen to see
  const chosenPriorities = new Set();   // empty = show every priority
  let reviewOnly = false;
  let page = 1;                         // the page being shown, starting at 1

  toolbar.hidden = false;
  showing.hidden = false;
  pager.hidden = false;

  function matchesFilters(ticket, words) {
    const matchesPriority = chosenPriorities.size === 0 || chosenPriorities.has(ticket.dataset.priority);
    const matchesReview = !reviewOnly || ticket.dataset.review === "yes";
    const matchesSearch = words.every(function (word) { return ticket.dataset.search.includes(word); });
    return matchesPriority && matchesReview && matchesSearch;
  }

  function update() {
    const words = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);

    // 1. Every ticket that matches the filters, in the order they're currently sorted
    const matching = Array.from(list.children).filter(function (t) { return matchesFilters(t, words); });

    // 2. Work out the pages, and keep the page number within range
    const pageCount = Math.max(1, Math.ceil(matching.length / PAGE_SIZE));
    page = Math.min(Math.max(page, 1), pageCount);
    const start = (page - 1) * PAGE_SIZE;
    const onThisPage = matching.slice(start, start + PAGE_SIZE);

    // 3. Show only this page's tickets
    tickets.forEach(function (ticket) { ticket.hidden = !onThisPage.includes(ticket); });

    // 4. Update the labels and buttons
    const filtered = matching.length < tickets.length;
    if (matching.length === 0) {
      showing.textContent = "Showing 0 tickets";
    } else if (matching.length === 1) {
      showing.textContent = filtered ? "Showing 1 matching ticket" : "Showing 1 ticket";
    } else {
      showing.textContent = "Showing " + (start + 1) + "–" + (start + onThisPage.length) + " of " +
        matching.length + (filtered ? " matching tickets" : " tickets");
    }
    pageLabel.textContent = "Page " + page + " of " + pageCount;
    prevButton.disabled = page === 1;
    nextButton.disabled = page === pageCount;
    pager.hidden = matching.length === 0;
    noMatch.hidden = matching.length > 0;
  }

  // Any change to the filters starts again from page 1
  function filtersChanged() {
    page = 1;
    update();
  }

  function reorder() {
    const order = {
      urgent: function (a, b) { return a.dataset.order - b.dataset.order; },   // the server's order
      newest: function (a, b) { return b.dataset.received.localeCompare(a.dataset.received); },
      oldest: function (a, b) { return a.dataset.received.localeCompare(b.dataset.received); },
    }[sort.value];
    tickets.slice().sort(order).forEach(function (ticket) { list.appendChild(ticket); });
    filtersChanged();
  }

  // Previous / Next page
  function goToPage(newPage) {
    page = newPage;
    update();
    pager.scrollIntoView({ block: "nearest" });   // keep the buttons in view after changing page
  }
  prevButton.addEventListener("click", function () { goToPage(page - 1); });
  nextButton.addEventListener("click", function () { goToPage(page + 1); });

  // Priority buttons: click to show only that priority; click more to add others
  priorityButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const code = button.dataset.priority;
      if (chosenPriorities.has(code)) chosenPriorities.delete(code);
      else chosenPriorities.add(code);
      button.setAttribute("aria-pressed", String(chosenPriorities.has(code)));
      filtersChanged();
    });
  });

  reviewFilter.addEventListener("click", function () {
    reviewOnly = !reviewOnly;
    reviewFilter.setAttribute("aria-pressed", String(reviewOnly));
    filtersChanged();
  });

  search.addEventListener("input", filtersChanged);
  sort.addEventListener("change", reorder);

  document.getElementById("clear-filters").addEventListener("click", function () {
    chosenPriorities.clear();
    reviewOnly = false;
    search.value = "";
    priorityButtons.concat(reviewFilter).forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
    filtersChanged();
    search.focus();
  });

  update();
})();
