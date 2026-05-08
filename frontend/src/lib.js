export const ENTRY_PATH = "/data/dictionary_entries.json.gz";
export const CORPUS_PATH = "/data/rendered_corpus.json.gz";
export const NAVARRO_PATH = "/data/navarro_dict.json.gz";
export const TOOLTIP_OVERRIDES_API_PATH = "/api/tooltip-overrides";
export const TOOLTIP_VIEWPORT_MARGIN = 12;
// Keep the legacy storage prefix so existing form-specific ROOT notes continue to match.
const ORTHOGRAPHIC_FORM_SCOPE_PREFIX = "ROOT_MORPHEME:";

export const FIELD_LABELS = {
  headword: "Headword",
  alias: "Alias",
  gloss: "Gloss",
  attestation: "Attestation",
  source: "Source",
  fulltext: "Full text",
};

export const QUALITY_LABELS = {
  exact: "Exact",
  prefix: "Prefix",
  phrase: "Phrase",
  contains: "Contains",
  all_terms: "All terms",
  partial_terms: "Partial terms",
};

export const METRIC_OPTIONS = {
  smart: { label: "Smart" },
  headword: { label: "Headword" },
  alias: { label: "Alias" },
  gloss: { label: "Gloss" },
  attestation: { label: "Attestation" },
  source: { label: "Source" },
  fulltext: { label: "Full Text" },
};

export const SORT_OPTIONS = {
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

export function compactWhitespace(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

export function normalizeText(text) {
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

  for (const item of items) {
    if (!item) {
      continue;
    }
    const preview = compactWhitespace(item.preview);
    const normalized = normalizeText(item.normalized || preview);
    if (!preview || !normalized) {
      continue;
    }
    const key = `${normalized}||${preview}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    output.push({ preview, normalized });
  }

  return output;
}

function compareNumbers(left, right) {
  return left - right;
}

function datasetRank(entry) {
  return entry.dataset === "lexicon" ? 0 : 1;
}

export function passesKindFilter(entry, activePosFilter) {
  if (!activePosFilter) {
    return true;
  }
  return activePosFilter.has(entry.part_of_speech?.kind || "");
}

export function isValidKey(value, options) {
  return Object.prototype.hasOwnProperty.call(options, value);
}

export function defaultDirectionFor(sortKey) {
  return SORT_OPTIONS[sortKey]?.defaultDirection || "asc";
}

export function getMetricLabel(metricKey) {
  return METRIC_OPTIONS[metricKey]?.label || METRIC_OPTIONS.smart.label;
}

export function getSortLabel(sortKey) {
  return SORT_OPTIONS[sortKey]?.label || SORT_OPTIONS.best_match.label;
}

export function getDirectionLabel(direction) {
  return direction === "desc" ? "descending" : "ascending";
}

export function readSettingsFromUrl() {
  if (typeof window === "undefined") {
    return {
      query: "",
      metric: "smart",
      sort: "best_match",
      direction: defaultDirectionFor("best_match"),
    };
  }

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

export function syncQuery(query, settings, { push = true } = {}) {
  if (typeof window === "undefined") {
    return;
  }

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
    window.history.pushState(null, "", url);
    return;
  }
  window.history.replaceState(null, "", url);
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
    new Blob([buffer]).stream().pipeThrough(new DecompressionStream("gzip")),
  );
  return JSON.parse(await decompressed.text());
}

export async function fetchMaybeGzipJson(path) {
  try {
    return await fetchGzipJson(path);
  } catch {
    const fallbackPath = path.replace(/\.gz$/, "");
    const response = await fetch(fallbackPath);
    if (!response.ok) {
      throw new Error(`Failed to load ${fallbackPath}: ${response.status}`);
    }
    return response.json();
  }
}

export async function fetchTooltipOverrides() {
  const response = await fetch(TOOLTIP_OVERRIDES_API_PATH, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Failed to load tooltip overrides: ${response.status}`);
  }
  return response.json();
}

export async function saveTooltipOverrideRequest(tags, text) {
  const response = await fetch(TOOLTIP_OVERRIDES_API_PATH, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ tags, text }),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || `Failed to save tooltip override: ${response.status}`);
  }
  return payload;
}

export function canonicalizeTooltipTags(tags) {
  return Array.from(
    new Set(
      (tags || [])
        .map((tag) => compactWhitespace(tag))
        .filter(Boolean)
        .filter((tag) => !/^deepest_node_/i.test(tag)),
    ),
  ).sort((left, right) => left.localeCompare(right));
}

export function buildTooltipScopeTags(tags, morpheme = "") {
  const scopeTags = canonicalizeTooltipTags(tags);
  const rawMorpheme = compactWhitespace(morpheme);
  if (!rawMorpheme) {
    return scopeTags;
  }

  return canonicalizeTooltipTags([
    ...scopeTags,
    `${ORTHOGRAPHIC_FORM_SCOPE_PREFIX}${rawMorpheme}`,
  ]);
}

export function getTooltipRequiredScopeTags(tags, morpheme = "") {
  return [];
}

export function formatTooltipScopeTag(tag) {
  if (typeof tag !== "string") {
    return "";
  }
  if (tag.startsWith(ORTHOGRAPHIC_FORM_SCOPE_PREFIX)) {
    return `Orthographic form: ${tag.slice(ORTHOGRAPHIC_FORM_SCOPE_PREFIX.length)}`;
  }
  return tag;
}

export function tooltipTagKey(tags) {
  return JSON.stringify(canonicalizeTooltipTags(tags));
}

export function normalizeTooltipOverrideEntry(entry) {
  const tags = canonicalizeTooltipTags(entry?.tags || []);
  return {
    tag_key: entry?.tag_key || tooltipTagKey(tags),
    tags,
    text: compactWhitespace(entry?.text || ""),
    created_at: entry?.created_at || "",
    updated_at: entry?.updated_at || "",
  };
}

export function replaceTooltipOverrideEntry(entries, entry) {
  const normalized = normalizeTooltipOverrideEntry(entry);
  const tagKey = tooltipTagKey(normalized.tags);
  const filteredEntries = entries.filter(
    (item) => tooltipTagKey(item.tags) !== tagKey,
  );
  return [normalized, ...filteredEntries];
}

export function removeTooltipOverrideEntry(entries, tags) {
  const tagKey = tooltipTagKey(tags);
  return entries.filter((item) => tooltipTagKey(item.tags) !== tagKey);
}

export function resolveTooltipOverrides(tags, entries, options = {}) {
  const canonicalTags = canonicalizeTooltipTags(tags);
  const requiredTags = canonicalizeTooltipTags(options.requiredTags || []);
  if (!canonicalTags.length || !entries.length) {
    return [];
  }

  const tagSet = new Set(canonicalTags);
  const matches = [];

  for (const entry of entries) {
    const entryTags = canonicalizeTooltipTags(entry.tags);
    if (!entryTags.length || !entryTags.every((tag) => tagSet.has(tag))) {
      continue;
    }
    if (requiredTags.length && !requiredTags.every((tag) => entryTags.includes(tag))) {
      continue;
    }
    matches.push({
      ...entry,
      tags: entryTags,
    });
  }

  matches.sort((left, right) => {
    if (right.tags.length !== left.tags.length) {
      return right.tags.length - left.tags.length;
    }
    return (right.updated_at || "").localeCompare(left.updated_at || "");
  });

  return matches;
}

export function resolveTooltipOverride(tags, entries, options = {}) {
  return resolveTooltipOverrides(tags, entries, options)[0] || null;
}

export function buildLineLookup(corpusPayload) {
  const lookup = new Map();
  for (const sourcePayload of Object.values(corpusPayload.sources || {})) {
    for (const line of sourcePayload.lines || []) {
      lookup.set(line.line_id, line);
    }
  }
  return lookup;
}

export function buildSearchDocuments(entries, lineLookup) {
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
      })),
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
      return {
        quality: "partial_terms",
        rank: 5 + (queryTokens.length - tokenHits.length),
      };
    }
  }

  return null;
}

function evaluateField(fieldKey, candidates, query, queryTokens) {
  let bestMatch = null;

  for (const candidate of candidates) {
    const match = candidateMatch(candidate.normalized, query, queryTokens);
    if (!match) {
      continue;
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
  }

  return bestMatch;
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
      left.entry.attestation_count || 0,
    );
  }

  return left.entry.normalized_headword.localeCompare(right.entry.normalized_headword);
}

function compareBySort(left, right, sortKey) {
  switch (sortKey) {
    case "best_match":
      return compareNumbers(
        left.score == null ? Number.MAX_SAFE_INTEGER : left.score,
        right.score == null ? Number.MAX_SAFE_INTEGER : right.score,
      );
    case "headword":
      return left.entry.normalized_headword.localeCompare(right.entry.normalized_headword);
    case "attestation_count":
      return compareNumbers(
        left.entry.attestation_count || 0,
        right.entry.attestation_count || 0,
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

export function searchEntries(query, settings, searchDocuments, activePosFilter) {
  const normalizedQuery = normalizeText(query);
  const queryTokens = normalizedQuery.split(" ").filter(Boolean);
  const scored = [];

  for (const documentEntry of searchDocuments) {
    if (!passesKindFilter(documentEntry.entry, activePosFilter)) {
      continue;
    }

    const weightedFields =
      SEARCH_FIELDS_BY_METRIC[settings.metric] || SEARCH_FIELDS_BY_METRIC.smart;
    let bestResult = null;

    for (const [fieldKey, fieldWeight] of weightedFields) {
      const match = evaluateField(
        fieldKey,
        documentEntry.fields[fieldKey] || [],
        normalizedQuery,
        queryTokens,
      );
      if (!match) {
        continue;
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
    }

    if (bestResult) {
      scored.push(bestResult);
    }
  }

  scored.sort((left, right) => compareResults(left, right, settings));
  return scored;
}

export function topEntries(settings, dictionaryEntries, activePosFilter) {
  const sortKey = settings.sort === "best_match" ? "attestation_count" : settings.sort;
  const direction =
    settings.sort === "best_match"
      ? defaultDirectionFor(sortKey)
      : settings.direction;

  return dictionaryEntries
    .filter(
      (entry) =>
        entry.dataset === "lexicon" &&
        Boolean(entry.normalized_headword) &&
        (entry.attestation_count || 0) > 0 &&
        passesKindFilter(entry, activePosFilter),
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
      }),
    )
    .slice(0, 20);
}

function parseNavarroDefinition(raw) {
  if (!raw) {
    return [];
  }

  const dashIndex = raw.indexOf("-");
  const body = dashIndex >= 0 ? raw.slice(dashIndex + 1) : raw;
  return body
    .split(/[;,]/)
    .map((segment) => segment.replace(/\(.*?\)/g, "").trim())
    .filter(Boolean);
}

export function buildNavarroIndex(entries) {
  const index = new Map();

  for (const { first_word, definition } of entries) {
    if (!first_word) {
      continue;
    }

    const tupiWords = parseNavarroDefinition(definition);
    for (const word of tupiWords) {
      const key = normalizeText(word);
      if (!key) {
        continue;
      }
      if (!index.has(key)) {
        index.set(key, []);
      }
      index.get(key).push(first_word);
    }
  }

  return index;
}

function rankNavarro(headwords, posHint) {
  if (!posHint || !headwords.length) {
    return headwords[0] || null;
  }

  const pos = posHint.toLowerCase();
  if (pos === "verb") {
    const verbs = headwords.filter((headword) => /[aei]r$/i.test(headword));
    if (verbs.length) {
      return verbs[0];
    }
  } else if (pos === "noun" || pos === "propernoun" || pos === "deverbal_noun") {
    const nouns = headwords.filter((headword) => !/[aei]r$/i.test(headword));
    if (nouns.length) {
      return nouns[0];
    }
  }

  return headwords[0];
}

function lookupNavarroRoot(navarroIndex, morpheme, posHint) {
  if (!navarroIndex) {
    return null;
  }

  const normalized = normalizeText(morpheme);
  if (!normalized) {
    return null;
  }

  if (navarroIndex.has(normalized)) {
    return rankNavarro(navarroIndex.get(normalized), posHint);
  }

  const prefixHits = [];
  for (const [key, headwords] of navarroIndex) {
    if (key.startsWith(normalized)) {
      prefixHits.push(...headwords);
    }
  }
  if (prefixHits.length) {
    return rankNavarro(prefixHits, posHint);
  }

  const suffixHits = [];
  for (const [key, headwords] of navarroIndex) {
    if (normalized.startsWith(key) && key.length >= 3) {
      suffixHits.push(...headwords);
    }
  }
  if (suffixHits.length) {
    return rankNavarro(suffixHits, posHint);
  }

  return null;
}

export function parseAnnotated(text) {
  const chunks = [];
  const regex = /([^\[]*)\[([^\]]+)\]/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    chunks.push({ text: match[1], tags: match[2].split(":") });
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    chunks.push({ text: text.slice(lastIndex), tags: [] });
  }

  return chunks;
}

export function buildMorphemeDetails(
  tags,
  morphemeMeta,
  morpheme,
  entryPosHint,
  navarroIndex,
) {
  const details = [];
  const headword = compactWhitespace(morphemeMeta?.headword || "");

  if (headword && normalizeText(headword) !== normalizeText(morpheme)) {
    details.push(`Headword: ${headword}`);
  }

  if (tags.includes("ROOT")) {
    const fallbackHeadword = lookupNavarroRoot(navarroIndex, morpheme, entryPosHint);
    if (
      fallbackHeadword &&
      normalizeText(fallbackHeadword) !== normalizeText(morpheme)
    ) {
      details.push(`Headword: ${fallbackHeadword}`);
    }
  }

  return details;
}

export function buildTooltipPayload(
  filteredTags,
  morphemeMeta,
  morpheme,
  entryPosHint,
  tooltipOverrides,
  navarroIndex,
) {
  const tags = canonicalizeTooltipTags(filteredTags);
  const scopeTags = buildTooltipScopeTags(tags, morpheme);
  const requiredScopeTags = getTooltipRequiredScopeTags(tags, morpheme);
  return {
    tags,
    scopeTags,
    requiredScopeTags,
    overrides: resolveTooltipOverrides(scopeTags, tooltipOverrides, {
      requiredTags: requiredScopeTags,
    }),
    detailLines: buildMorphemeDetails(
      tags,
      morphemeMeta,
      morpheme,
      entryPosHint,
      navarroIndex,
    ),
  };
}

export function tagToColors(tag) {
  let hash = 5381;
  for (let index = 0; index < tag.length; index += 1) {
    hash = ((hash << 5) + hash + tag.charCodeAt(index)) & 0x7fffffff;
  }
  const hue = (hash * 137) % 360;
  return {
    color: `hsl(${hue}, 58%, 30%)`,
    bg: `hsl(${hue}, 55%, 92%)`,
  };
}

export function resetTooltipPosition(chunk) {
  if (!chunk) {
    return;
  }

  chunk.classList.remove("tooltip-below");
  chunk.classList.remove("tooltip-edge-left");
  chunk.classList.remove("tooltip-edge-right");
  const tip = chunk.querySelector(".morpheme-tooltip");
  if (tip) {
    tip.style.removeProperty("--tooltip-shift-x");
  }
}

export function positionTooltipInViewport(
  chunk,
  tip,
  viewportMargin = TOOLTIP_VIEWPORT_MARGIN,
) {
  if (!chunk || !tip || !tip.isConnected) {
    return;
  }

  chunk.classList.remove("tooltip-below");
  chunk.classList.remove("tooltip-edge-left");
  chunk.classList.remove("tooltip-edge-right");
  tip.style.setProperty("--tooltip-shift-x", "0px");

  let rect = tip.getBoundingClientRect();
  const chunkRect = chunk.getBoundingClientRect();
  const spaceAbove = chunkRect.top - viewportMargin;
  const spaceBelow = window.innerHeight - chunkRect.bottom - viewportMargin;

  if (rect.top < viewportMargin && spaceBelow > spaceAbove) {
    chunk.classList.add("tooltip-below");
    rect = tip.getBoundingClientRect();
  }

  if (rect.left < viewportMargin) {
    chunk.classList.add("tooltip-edge-left");
    rect = tip.getBoundingClientRect();
  } else if (rect.right > window.innerWidth - viewportMargin) {
    chunk.classList.add("tooltip-edge-right");
    rect = tip.getBoundingClientRect();
  }

  let shiftX = 0;
  if (rect.left < viewportMargin) {
    shiftX = viewportMargin - rect.left;
  } else if (rect.right > window.innerWidth - viewportMargin) {
    shiftX = window.innerWidth - viewportMargin - rect.right;
  }

  tip.style.setProperty("--tooltip-shift-x", `${shiftX}px`);
}
