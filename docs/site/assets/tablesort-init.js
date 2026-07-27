// Sortable tables, per the mkdocs-material recipe. `document$` is Material's
// own observable and fires again after every instant-navigation page load, so
// tables on a page reached by clicking a link get wired up too.
//
// `table:not([class])` skips tables the theme or a plugin generated for its
// own purposes: the summary tables in the rule catalog are plain markdown and
// carry no class, and those are the ones worth sorting.
document$.subscribe(function () {
  document.querySelectorAll('article table:not([class])').forEach(function (table) {
    new Tablesort(table);
  });
});
