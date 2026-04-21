(() => {
  "use strict";

  const ENTRY_PATH = "./data/dictionary_entries.json.gz";
  const CORPUS_PATH = "./data/rendered_corpus.json.gz";

  const FIELD_LABELS = {
    headword: "Headword",
    alias: "Alias",
    gloss: "Gloss",
    attestation: "Attestation",
    source: "Source",
    fulltext: "Full text",
  };

  const QUALITY_LABELS = {
    exact: "Exact",
    prefix: "Prefix",
    phrase: "Phrase",
    contains: "Contains",
    all_terms: "All terms",
    partial_terms: "Partial terms",
  };

  const METRIC_OPTIONS = {
    smart: { label: "Smart" },
    headword: { label: "Headword" },
    alias: { label: "Alias" },
    gloss: { label: "Gloss" },
    attestation: { label: "Attestation" },
    source: { label: "Source" },
    fulltext: { label: "Full Text" },
  };

  const SORT_OPTIONS = {
    best_match: { label: "Best Match", defaultDirection: "asc" },
    headword: { label: "Headword", defaultDirection: "asc" },
    attestation_count: { label: "Attestation Count", defaultDirection: "desc" },
    source_count: { label: "Source Count", defaultDirection: "desc" },
    dataset: { label: "Dataset", defaultDirection: "asc" },
  };

  const SEARCH_FIELDS_BY_METRIC = {
    smart: [
      ["headword", 0],
      ["alias", 100],
      ["gloss", 200],
      ["attestation", 300],
      ["source", 400],
      ["fulltext", 500],
    ],
    headword: [["headword", 0]],
    alias: [["alias", 0]],
    gloss: [["gloss", 0]],
    attestation: [["attestation", 0]],
    source: [["source", 0]],
    fulltext: [["fulltext", 0]],
  };

  const searchForm = document.getElementById("search-form");
  const searchInput = document.getElementById("search-input");
  const metricSelect = document.getElementById("metric-select");
  const sortSelect = document.getElementById("sort-select");
  const directionSelect = document.getElementById("direction-select");
  const clearButton = document.getElementById("clear-button");
  const summary = document.getElementById("summary");
  const resultsRoot = document.getElementById("results");

  const metaEntryCount = document.getElementById("meta-entry-count");
  const metaLineCount = document.getElementById("meta-line-count");
  const metaSourceCount = document.getElementById("meta-source-count");
  const metaGeneratedAt = document.getElementById("meta-generated-at");

  let dictionaryEntries = [];
  let renderedCorpus = null;
  let lineLookup = new Map();
  let searchDocuments = [];
  let ready = false;

  function compactWhitespace(text) {
    return String(text || "").replace(/\s+/g, " ").trim();
  }

  function normalizeText(text) {
    return compactWhitespace(text)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/’/g, "'")
      .replace(/[^0-9a-zà-ÿ' -]+/gi, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function escapeRegExp(text) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function uniqueCandidates(items) {
    const seen = new Set();
    const output = [];
    items.forEach((item) => {
      if (!item) {
        return;
      }
      const preview = compactWhitespace(item.preview);
      const normalized = normalizeText(item.normalized || preview);
      if (!preview || !normalized) {
        return;
      }
      const key = `${normalized}||${preview}`;
      if (seen.has(key)) {
        return;
      }
      seen.add(key);
      output.push({ preview, normalized });
    });
    return output;
  }

  function compareNumbers(left, right) {
    return left - right;
  }

  function datasetRank(entry) {
    return entry.dataset === "lexicon" ? 0 : 1;
  }

  function isValidKey(value, options) {
    return Object.prototype.hasOwnProperty.call(options, value);
  }

  function defaultDirectionFor(sortKey) {
    return SORT_OPTIONS[sortKey]?.defaultDirection || "asc";
  }

  function getMetricLabel(metricKey) {
    return METRIC_OPTIONS[metricKey]?.label || METRIC_OPTIONS.smart.label;
  }

  function getSortLabel(sortKey) {
    return SORT_OPTIONS[sortKey]?.label || SORT_OPTIONS.best_match.label;
  }

  function getDirectionLabel(direction) {
    return direction === "desc" ? "descending" : "ascending";
  }

  function getCurrentSettings() {
    const metric = isValidKey(metricSelect.value, METRIC_OPTIONS)
      ? metricSelect.value
      : "smart";
    const sort = isValidKey(sortSelect.value, SORT_OPTIONS)
      ? sortSelect.value
      : "best_match";
    const direction = directionSelect.value === "desc" ? "desc" : "asc";
    return { metric, sort, direction };
  }

  function applySettings(settings) {
    metricSelect.value = isValidKey(settings.metric, METRIC_OPTIONS)
      ? settings.metric
      : "smart";
    sortSelect.value = isValidKey(settings.sort, SORT_OPTIONS)
      ? settings.sort
      : "best_match";
    directionSelect.value = settings.direction === "desc" ? "desc" : "asc";
  }

  function readSettingsFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const metric = isValidKey(params.get("metric"), METRIC_OPTIONS)
      ? params.get("metric")
      : "smart";
    const sort = isValidKey(params.get("sort"), SORT_OPTIONS)
      ? params.get("sort")
      : "best_match";
    const direction = params.get("dir") === "desc" ? "desc" : defaultDirectionFor(sort);
    const query = compactWhitespace(params.get("query") || "");
    return { query, metric, sort, direction };
  }

  async function fetchMaybeGzipJson(path) {
    try {
      return await fetchGzipJson(path);
    } catch (_error) {
      const fallbackPath = path.replace(/\.gz$/, "");
      const response = await fetch(fallbackPath);
      if (!response.ok) {
        throw new Error(`Failed to load ${fallbackPath}: ${response.status}`);
      }
      return response.json();
    }
  }

  async function fetchGzipJson(path) {
    const response = await fetch(path);
    if (!response.ok) {
      throw new Error(`Failed to load ${path}: ${response.status}`);
    }
    const buffer = await response.arrayBuffer();
    if (typeof DecompressionStream !== "function") {
      throw new Error("DecompressionStream not supported");
    }
    const decompressed = new Response(
      new Blob([buffer]).stream().pipeThrough(new DecompressionStream("gzip"))
    );
    return JSON.parse(await decompressed.text());
  }

  function buildLineLookup(corpusPayload) {
    const lookup = new Map();
    Object.values(corpusPayload.sources || {}).forEach((sourcePayload) => {
      (sourcePayload.lines || []).forEach((line) => {
        lookup.set(line.line_id, line);
      });
    });
    return lookup;
  }

  function buildSearchDocuments(entries) {
    return entries.map((entry) => {
      const attestationLines = (entry.attestations || [])
        .map((attestation) => lineLookup.get(attestation.line_id))
        .filter(Boolean);

      const headword = uniqueCandidates([
        { preview: entry.headword, normalized: entry.headword },
      ]);

      const aliases = uniqueCandidates(
        (entry.aliases || []).map((alias) => ({
          preview: alias,
          normalized: alias,
        }))
      );

      const glosses = uniqueCandidates([
        ...((entry.definition?.glosses || []).map((gloss) => ({
          preview: gloss,
          normalized: gloss,
        }))),
        ...((entry.definition?.qualifiers || []).map((qualifier) => ({
          preview: qualifier,
          normalized: qualifier,
        }))),
        {
          preview: entry.definition?.raw || "",
          normalized: entry.definition?.raw || "",
        },
      ]);

      const attestationCandidates = uniqueCandidates([
        ...attestationLines.map((line) => ({
          preview: line.surface,
          normalized: line.surface,
        })),
        ...attestationLines.map((line) => ({
          preview: `${line.source}:${line.expression_index}`,
          normalized: line.annotated,
        })),
      ]);

      const sources = uniqueCandidates([
        ...((entry.source_counts || []).map((item) => ({
          preview: item.source,
          normalized: item.source,
        }))),
        ...attestationLines.map((line) => ({
          preview: line.source,
          normalized: line.source,
        })),
      ]);

      const fulltext = uniqueCandidates([
        {
          preview: entry.definition?.raw || entry.headword,
          normalized: [
            entry.headword,
            ...(entry.aliases || []),
            ...(entry.definition?.qualifiers || []),
            ...(entry.definition?.glosses || []),
            entry.definition?.raw || "",
            ...(entry.source_counts || []).map((item) => item.source),
            ...attestationLines.map((line) => line.surface),
            ...attestationLines.map((line) => line.annotated),
          ].join(" "),
        },
      ]);

      return {
        entry,
        sourceCount: (entry.source_counts || []).length,
        fields: {
          headword,
          alias: aliases,
          gloss: glosses,
          attestation: attestationCandidates,
          source: sources,
          fulltext,
        },
      };
    });
  }

  function candidateMatch(normalizedValue, query, queryTokens) {
    if (!normalizedValue || !query) {
      return null;
    }
    if (normalizedValue === query) {
      return { quality: "exact", rank: 0 };
    }
    if (normalizedValue.startsWith(query)) {
      return { quality: "prefix", rank: 1 };
    }
    const phraseRegex = new RegExp(`(^|\\s)${escapeRegExp(query)}(?=\\s|$)`, "i");
    if (phraseRegex.test(normalizedValue)) {
      return { quality: "phrase", rank: 2 };
    }
    if (normalizedValue.includes(query)) {
      return { quality: "contains", rank: 3 };
    }
    if (queryTokens.length > 1) {
      const tokenHits = queryTokens.filter((token) => normalizedValue.includes(token));
      if (tokenHits.length === queryTokens.length) {
        return { quality: "all_terms", rank: 4 };
      }
      if (tokenHits.length > 0) {
        return { quality: "partial_terms", rank: 5 + (queryTokens.length - tokenHits.length) };
      }
    }
    return null;
  }

  function evaluateField(fieldKey, candidates, query, queryTokens) {
    let bestMatch = null;
    candidates.forEach((candidate) => {
      const match = candidateMatch(candidate.normalized, query, queryTokens);
      if (!match) {
        return;
      }
      const proposal = {
        field: fieldKey,
        fieldLabel: FIELD_LABELS[fieldKey],
        quality: match.quality,
        qualityRank: match.rank,
        preview: candidate.preview,
        normalized: candidate.normalized,
      };
      if (
        !bestMatch ||
        proposal.qualityRank < bestMatch.qualityRank ||
        (proposal.qualityRank === bestMatch.qualityRank &&
          proposal.normalized.length < bestMatch.normalized.length)
      ) {
        bestMatch = proposal;
      }
    });
    return bestMatch;
  }

  function searchEntries(query, settings) {
    const normalizedQuery = normalizeText(query);
    const queryTokens = normalizedQuery.split(" ").filter(Boolean);
    const scored = [];

    searchDocuments.forEach((documentEntry) => {
      const weightedFields = SEARCH_FIELDS_BY_METRIC[settings.metric] || SEARCH_FIELDS_BY_METRIC.smart;
      let bestResult = null;

      weightedFields.forEach(([fieldKey, fieldWeight]) => {
        const match = evaluateField(
          fieldKey,
          documentEntry.fields[fieldKey] || [],
          normalizedQuery,
          queryTokens
        );
        if (!match) {
          return;
        }
        const score = fieldWeight + match.qualityRank * 10;
        const proposal = {
          entry: documentEntry.entry,
          score,
          match,
          sourceCount: documentEntry.sourceCount,
        };
        if (
          !bestResult ||
          proposal.score < bestResult.score ||
          (proposal.score === bestResult.score &&
            proposal.match.preview.length < bestResult.match.preview.length)
        ) {
          bestResult = proposal;
        }
      });

      if (bestResult) {
        scored.push(bestResult);
      }
    });

    scored.sort((left, right) => compareResults(left, right, settings));
    return scored;
  }

  function compareFallback(left, right) {
    const leftScore = left.score == null ? Number.MAX_SAFE_INTEGER : left.score;
    const rightScore = right.score == null ? Number.MAX_SAFE_INTEGER : right.score;
    if (leftScore !== rightScore) {
      return compareNumbers(leftScore, rightScore);
    }
    const datasetDelta = compareNumbers(datasetRank(left.entry), datasetRank(right.entry));
    if (datasetDelta !== 0) {
      return datasetDelta;
    }
    if ((right.entry.attestation_count || 0) !== (left.entry.attestation_count || 0)) {
      return compareNumbers(
        right.entry.attestation_count || 0,
        left.entry.attestation_count || 0
      );
    }
    return left.entry.normalized_headword.localeCompare(right.entry.normalized_headword);
  }

  function compareBySort(left, right, sortKey) {
    switch (sortKey) {
      case "best_match":
        return compareNumbers(
          left.score == null ? Number.MAX_SAFE_INTEGER : left.score,
          right.score == null ? Number.MAX_SAFE_INTEGER : right.score
        );
      case "headword":
        return left.entry.normalized_headword.localeCompare(right.entry.normalized_headword);
      case "attestation_count":
        return compareNumbers(
          left.entry.attestation_count || 0,
          right.entry.attestation_count || 0
        );
      case "source_count":
        return compareNumbers(left.sourceCount || 0, right.sourceCount || 0);
      case "dataset":
        return compareNumbers(datasetRank(left.entry), datasetRank(right.entry));
      default:
        return 0;
    }
  }

  function compareResults(left, right, settings) {
    const primary = compareBySort(left, right, settings.sort);
    if (primary !== 0) {
      return settings.direction === "desc" ? -primary : primary;
    }
    return compareFallback(left, right);
  }

  function topEntries(settings) {
    const sortKey = settings.sort === "best_match" ? "attestation_count" : settings.sort;
    const direction = settings.sort === "best_match"
      ? defaultDirectionFor(sortKey)
      : settings.direction;
    return dictionaryEntries
      .filter(
        (entry) =>
          entry.dataset === "lexicon" &&
          Boolean(entry.normalized_headword) &&
          (entry.attestation_count || 0) > 0
      )
      .map((entry) => ({
        entry,
        score: null,
        match: null,
        sourceCount: (entry.source_counts || []).length,
      }))
      .sort((left, right) =>
        compareResults(left, right, {
          metric: settings.metric,
          sort: sortKey,
          direction,
        })
      )
      .slice(0, 20);
  }

  function clearResults() {
    resultsRoot.replaceChildren();
  }

  function renderMessage(message, className) {
    clearResults();
    const node = document.createElement("div");
    node.className = className;
    node.textContent = message;
    resultsRoot.appendChild(node);
  }

  function makeChip(text, className) {
    const chip = document.createElement("span");
    chip.className = className;
    chip.textContent = text;
    return chip;
  }

  function renderDefinition(definition) {
    const wrapper = document.createElement("section");

    if ((definition.qualifiers || []).length) {
      const label = document.createElement("span");
      label.className = "field-label";
      label.textContent = "Qualifiers";
      wrapper.appendChild(label);

      const qualifierRow = document.createElement("div");
      qualifierRow.className = "entry-tags";
      definition.qualifiers.forEach((qualifier) => {
        qualifierRow.appendChild(makeChip(qualifier, "tag"));
      });
      wrapper.appendChild(qualifierRow);
    }

    const glossLabel = document.createElement("span");
    glossLabel.className = "field-label";
    glossLabel.textContent = "Glosses";
    wrapper.appendChild(glossLabel);

    const glossList = document.createElement("div");
    glossList.className = "gloss-list";
    const glosses = definition.glosses || [];
    if (!glosses.length) {
      const glossNode = document.createElement("span");
      glossNode.className = "gloss";
      glossNode.textContent = "Definition pending";
      glossList.appendChild(glossNode);
    }
    glosses.forEach((gloss) => {
      const glossNode = document.createElement("span");
      glossNode.className = "gloss";
      glossNode.textContent = gloss;
      glossList.appendChild(glossNode);
    });
    wrapper.appendChild(glossList);
    return wrapper;
  }

  function renderAliases(entry) {
    if (!entry.aliases || !entry.aliases.length) {
      return null;
    }
    const section = document.createElement("section");
    const label = document.createElement("span");
    label.className = "field-label";
    label.textContent = "Aliases";
    section.appendChild(label);

    const aliases = document.createElement("div");
    aliases.className = "aliases";
    aliases.textContent = entry.aliases.join(", ");
    section.appendChild(aliases);
    return section;
  }

  function renderSourceCounts(entry) {
    if (!entry.source_counts || !entry.source_counts.length) {
      return null;
    }
    const section = document.createElement("section");
    const label = document.createElement("span");
    label.className = "field-label";
    label.textContent = "Sources";
    section.appendChild(label);

    const row = document.createElement("div");
    row.className = "source-chips";
    entry.source_counts.forEach((item) => {
      row.appendChild(makeChip(`${item.source} (${item.count})`, "source-chip"));
    });
    section.appendChild(row);
    return section;
  }

  function renderMatchDetails(result) {
    if (!result.match) {
      return null;
    }
    const section = document.createElement("section");
    const label = document.createElement("span");
    label.className = "field-label";
    label.textContent = "Matched";
    section.appendChild(label);

    const matchPreview = document.createElement("div");
    matchPreview.className = "aliases";
    matchPreview.textContent = `${result.match.fieldLabel} · ${QUALITY_LABELS[result.match.quality]}`;
    if (result.match.preview && result.match.preview !== result.entry.headword) {
      matchPreview.textContent += ` · ${result.match.preview}`;
    }
    section.appendChild(matchPreview);
    return section;
  }

  function renderAttestations(entry) {
    if (!entry.attestations || !entry.attestations.length) {
      return null;
    }
    const section = document.createElement("section");
    section.className = "attestations";

    const details = document.createElement("details");
    if (entry.attestation_count <= 3) {
      details.open = true;
    }

    const summaryNode = document.createElement("summary");
    summaryNode.textContent = `Attestations (${entry.attestation_count})`;
    details.appendChild(summaryNode);

    const list = document.createElement("div");
    list.className = "attestation-list";
    entry.attestations.forEach((attestation) => {
      const line = lineLookup.get(attestation.line_id);
      if (!line) {
        return;
      }
      const card = document.createElement("article");
      card.className = "attestation-card";

      const chipRow = document.createElement("div");
      chipRow.className = "source-chips";
      chipRow.appendChild(
        makeChip(`${line.source}:${line.expression_index}`, "source-chip")
      );
      card.appendChild(chipRow);

      const surface = document.createElement("p");
      surface.className = "attestation-surface";
      surface.textContent = line.surface;
      card.appendChild(surface);

      const annotated = document.createElement("pre");
      annotated.className = "attestation-annotated";
      annotated.textContent = line.annotated;
      card.appendChild(annotated);

      list.appendChild(card);
    });
    details.appendChild(list);
    section.appendChild(details);
    return section;
  }

  function renderEntryCard(result) {
    const { entry, score } = result;
    const article = document.createElement("article");
    article.className = "entry-card";

    const top = document.createElement("div");
    top.className = "entry-top";

    const heading = document.createElement("div");
    heading.className = "entry-heading";
    const title = document.createElement("h2");
    title.textContent = entry.headword;
    heading.appendChild(title);
    top.appendChild(heading);

    const badges = document.createElement("div");
    badges.className = "entry-badges";
    badges.appendChild(
      makeChip(entry.dataset === "lexicon" ? "Lexicon" : "Navarro supplement", "badge")
    );
    if (entry.part_of_speech && entry.part_of_speech.kind) {
      badges.appendChild(makeChip(entry.part_of_speech.kind, "badge"));
    }
    if (entry.metadata && entry.metadata.definition_missing) {
      badges.appendChild(makeChip("Gloss pending", "badge"));
    }
    if (result.match) {
      badges.appendChild(
        makeChip(
          `${result.match.fieldLabel}: ${QUALITY_LABELS[result.match.quality]}`,
          "badge metric"
        )
      );
    }
    if (score !== null && score <= 1) {
      badges.appendChild(makeChip("Exact match", "badge exact"));
    }
    top.appendChild(badges);

    const body = document.createElement("div");
    body.className = "entry-body";
    body.appendChild(renderDefinition(entry.definition));

    const matchSection = renderMatchDetails(result);
    if (matchSection) {
      body.appendChild(matchSection);
    }

    const aliasesSection = renderAliases(entry);
    if (aliasesSection) {
      body.appendChild(aliasesSection);
    }

    const sourcesSection = renderSourceCounts(entry);
    if (sourcesSection) {
      body.appendChild(sourcesSection);
    }

    const attestationsSection = renderAttestations(entry);
    if (attestationsSection) {
      body.appendChild(attestationsSection);
    }

    article.appendChild(top);
    article.appendChild(body);
    return article;
  }

  function setSummary(text) {
    summary.textContent = text;
  }

  function renderResultSet(resultSet) {
    clearResults();
    if (!resultSet.length) {
      renderMessage("No results found for that query.", "empty-state");
      return;
    }
    const fragment = document.createDocumentFragment();
    resultSet.forEach((result) => {
      fragment.appendChild(renderEntryCard(result));
    });
    resultsRoot.appendChild(fragment);
  }

  function syncQuery(query, settings, { push = true } = {}) {
    const url = new URL(window.location.href);
    if (query) {
      url.searchParams.set("query", query);
    } else {
      url.searchParams.delete("query");
    }
    url.searchParams.set("metric", settings.metric);
    url.searchParams.set("sort", settings.sort);
    url.searchParams.set("dir", settings.direction);

    const defaultState =
      !query &&
      settings.metric === "smart" &&
      settings.sort === "best_match" &&
      settings.direction === defaultDirectionFor("best_match");

    if (defaultState) {
      url.searchParams.delete("metric");
      url.searchParams.delete("sort");
      url.searchParams.delete("dir");
    }

    if (push) {
      history.pushState(null, "", url);
    } else {
      history.replaceState(null, "", url);
    }
  }

  function runSearch(query, options = {}) {
    const compactQuery = compactWhitespace(query);
    const settings = options.settings || getCurrentSettings();
    applySettings(settings);
    searchInput.value = compactQuery;

    if (!compactQuery) {
      const defaults = topEntries(settings);
      const displaySort = settings.sort === "best_match" ? "attestation_count" : settings.sort;
      const displayDirection = settings.sort === "best_match"
        ? defaultDirectionFor(displaySort)
        : settings.direction;
      setSummary(
        `Loaded ${dictionaryEntries.length} structured entries and ${renderedCorpus.meta.line_count} rendered corpus lines. ` +
          `Showing attested lexicon entries sorted by ${getSortLabel(displaySort)} (${getDirectionLabel(displayDirection)}).`
      );
      renderResultSet(defaults);
      syncQuery("", settings, options);
      return;
    }

    const results = searchEntries(compactQuery, settings);
    setSummary(
      `Found ${results.length} result${results.length === 1 ? "" : "s"} for "${compactQuery}" ` +
        `using ${getMetricLabel(settings.metric)}, sorted by ${getSortLabel(settings.sort)} (${getDirectionLabel(settings.direction)}).`
    );
    renderResultSet(results);
    syncQuery(compactQuery, settings, options);
  }

  async function bootstrap() {
    try {
      const initialState = readSettingsFromUrl();
      applySettings(initialState);

      const [entryPayload, corpusPayload] = await Promise.all([
        fetchMaybeGzipJson(ENTRY_PATH),
        fetchMaybeGzipJson(CORPUS_PATH),
      ]);
      dictionaryEntries = entryPayload.entries || [];
      renderedCorpus = corpusPayload;
      lineLookup = buildLineLookup(corpusPayload);
      searchDocuments = buildSearchDocuments(dictionaryEntries);
      ready = true;

      metaEntryCount.textContent = String(entryPayload.meta.entry_count || dictionaryEntries.length);
      metaLineCount.textContent = String(corpusPayload.meta.line_count || 0);
      metaSourceCount.textContent = String(corpusPayload.meta.source_count || 0);
      metaGeneratedAt.textContent = compactWhitespace(
        entryPayload.meta.generated_at || corpusPayload.meta.generated_at || "-"
      );

      runSearch(initialState.query, {
        push: false,
        settings: initialState,
      });
    } catch (error) {
      console.error(error);
      renderMessage("Failed to load dictionary artifacts.", "error-state");
      setSummary("Dictionary artifacts could not be loaded.");
    }
  }

  searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!ready) {
      return;
    }
    runSearch(searchInput.value);
  });

  metricSelect.addEventListener("change", () => {
    if (!ready) {
      return;
    }
    runSearch(searchInput.value);
  });

  sortSelect.addEventListener("change", () => {
    directionSelect.value = defaultDirectionFor(sortSelect.value);
    if (!ready) {
      return;
    }
    runSearch(searchInput.value);
  });

  directionSelect.addEventListener("change", () => {
    if (!ready) {
      return;
    }
    runSearch(searchInput.value);
  });

  clearButton.addEventListener("click", () => {
    if (!ready) {
      return;
    }
    runSearch("", { settings: getCurrentSettings() });
    searchInput.focus();
  });

  window.addEventListener("popstate", () => {
    if (!ready) {
      return;
    }
    const state = readSettingsFromUrl();
    runSearch(state.query, {
      push: false,
      settings: state,
    });
  });

  bootstrap();
})();
