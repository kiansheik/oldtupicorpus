import { Fragment, useEffect, useRef, useState } from "react";
import {
  CORPUS_PATH,
  ENTRY_PATH,
  METRIC_OPTIONS,
  NAVARRO_PATH,
  QUALITY_LABELS,
  SORT_OPTIONS,
  buildLineLookup,
  buildNavarroIndex,
  buildSearchDocuments,
  buildTooltipPayload,
  canonicalizeTooltipTags,
  compactWhitespace,
  defaultDirectionFor,
  fetchMaybeGzipJson,
  fetchTooltipOverrides,
  formatTooltipScopeTag,
  getDirectionLabel,
  getMetricLabel,
  getSortLabel,
  isValidKey,
  normalizeTooltipOverrideEntry,
  parseAnnotated,
  positionTooltipInViewport,
  readSettingsFromUrl,
  removeTooltipOverrideEntry,
  replaceTooltipOverrideEntry,
  resetTooltipPosition,
  saveTooltipOverrideRequest,
  searchEntries,
  syncQuery,
  tagToColors,
  topEntries,
} from "./lib";

const INITIAL_URL_STATE = readSettingsFromUrl();
const TOOLTIP_CLOSE_DELAY_MS = 20;
const NEW_TOOLTIP_NOTE_KEY = "__new__";

function makeChip(text, className) {
  return (
    <span className={className}>
      {text}
    </span>
  );
}

function MorphemeChunk({
  chunkId,
  morpheme,
  payload,
  openTooltipId,
  setOpenTooltipId,
  tooltipEditingAvailable,
  onSaveTooltipOverride,
}) {
  const chunkRef = useRef(null);
  const tooltipRef = useRef(null);
  const closeTimeoutRef = useRef(null);
  const [isHoverVisible, setIsHoverVisible] = useState(false);
  const [editingNoteKey, setEditingNoteKey] = useState(null);
  const [selectedTags, setSelectedTags] = useState([]);
  const [draftText, setDraftText] = useState("");
  const [status, setStatus] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const isOpen = openTooltipId === chunkId;
  const isTooltipVisible = isOpen || isHoverVisible;
  const editing = editingNoteKey !== null;
  const payloadSignature = [
    payload.tags.join("|"),
    payload.scopeTags.join("|"),
    payload.detailLines.join("|"),
    payload.overrides.map((note) => `${note.tag_key}:${note.updated_at}:${note.text}`).join("||"),
  ].join("::");

  useEffect(() => {
    return () => {
      if (closeTimeoutRef.current) {
        window.clearTimeout(closeTimeoutRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (isOpen) {
      return undefined;
    }
    setEditingNoteKey(null);
    setStatus("");
    setIsSaving(false);
    setIsHoverVisible(false);
    resetTooltipPosition(chunkRef.current);
    return undefined;
  }, [isOpen]);

  useEffect(() => {
    if (!isTooltipVisible) {
      return undefined;
    }

    const schedulePosition = () => {
      window.requestAnimationFrame(() => {
        positionTooltipInViewport(chunkRef.current, tooltipRef.current);
      });
    };

    schedulePosition();
    window.addEventListener("resize", schedulePosition);
    window.addEventListener("scroll", schedulePosition, true);
    return () => {
      window.removeEventListener("resize", schedulePosition);
      window.removeEventListener("scroll", schedulePosition, true);
    };
  }, [editing, isTooltipVisible, payloadSignature]);

  const clearPendingClose = () => {
    if (!closeTimeoutRef.current) {
      return;
    }
    window.clearTimeout(closeTimeoutRef.current);
    closeTimeoutRef.current = null;
  };

  const handlePreviewPosition = () => {
    window.requestAnimationFrame(() => {
      positionTooltipInViewport(chunkRef.current, tooltipRef.current);
    });
  };

  const showTooltipPreview = () => {
    clearPendingClose();
    setIsHoverVisible(true);
    handlePreviewPosition();
  };

  const scheduleTooltipClose = (event) => {
    const nextTarget = event?.relatedTarget;
    if (nextTarget instanceof Node && chunkRef.current?.contains(nextTarget)) {
      return;
    }
    if (isOpen) {
      return;
    }
    clearPendingClose();
    closeTimeoutRef.current = window.setTimeout(() => {
      setIsHoverVisible(false);
      closeTimeoutRef.current = null;
    }, TOOLTIP_CLOSE_DELAY_MS);
  };

  const handleOpen = (event) => {
    event.stopPropagation();
    clearPendingClose();
    setIsHoverVisible(true);
    setOpenTooltipId(chunkId);
    handlePreviewPosition();
  };

  const handleStartEdit = (event, note = null) => {
    event.stopPropagation();
    clearPendingClose();
    setSelectedTags(
      canonicalizeTooltipTags([
        ...(note?.tags || payload.tags),
        ...payload.requiredScopeTags,
      ]),
    );
    setDraftText(note?.text || "");
    setStatus("");
    setIsHoverVisible(true);
    setEditingNoteKey(note?.tag_key || NEW_TOOLTIP_NOTE_KEY);
    setOpenTooltipId(chunkId);
  };

  const handleCancel = (event) => {
    event.stopPropagation();
    setEditingNoteKey(null);
    setStatus("");
  };

  const handleSave = async (event) => {
    event.stopPropagation();
    const tagsToSave = canonicalizeTooltipTags([
      ...selectedTags,
      ...payload.requiredScopeTags,
    ]);

    if (!tagsToSave.length) {
      setStatus("Select at least one tag.");
      return;
    }

    setStatus("Saving...");
    setIsSaving(true);
    try {
      await onSaveTooltipOverride(tagsToSave, draftText);
      setEditingNoteKey(null);
      setStatus("");
      setOpenTooltipId(null);
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Failed to save note.");
      setIsSaving(false);
    }
  };

  const { color, bg } = tagToColors(payload.tags[0] || "ANNOTATED");

  return (
    <span
      ref={chunkRef}
      className={`morpheme-chunk${isTooltipVisible ? " tooltip-visible" : ""}`}
      style={{
        "--chunk-color": color,
        "--chunk-bg": bg,
      }}
      tabIndex={0}
      role="button"
      aria-expanded={isTooltipVisible ? "true" : "false"}
      onMouseEnter={showTooltipPreview}
      onMouseLeave={scheduleTooltipClose}
      onFocus={showTooltipPreview}
      onBlur={(event) => {
        if (event.currentTarget.contains(event.relatedTarget)) {
          return;
        }
        scheduleTooltipClose();
      }}
      onClick={handleOpen}
      onKeyDown={(event) => {
        if (event.target !== event.currentTarget) {
          if (event.key === "Escape") {
            event.stopPropagation();
            setOpenTooltipId(null);
          }
          return;
        }

        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          handleOpen(event);
        } else if (event.key === "Escape") {
          event.preventDefault();
          setOpenTooltipId(null);
        }
      }}
    >
      {morpheme}
      <span
        ref={tooltipRef}
        className="morpheme-tooltip"
        onMouseEnter={showTooltipPreview}
        onMouseLeave={scheduleTooltipClose}
        onClick={(event) => {
          event.stopPropagation();
          clearPendingClose();
          setIsHoverVisible(true);
          setOpenTooltipId(chunkId);
        }}
      >
        {editing ? (
          <section className="morpheme-tooltip-section">
            <div className="morpheme-tooltip-label">
              {editingNoteKey === NEW_TOOLTIP_NOTE_KEY ? "Add note" : "Edit note"}
            </div>
            <div className="morpheme-tooltip-hint">
              This note will appear anywhere all checked tags are present.
            </div>
            <div className="morpheme-tooltip-scope-list">
              {payload.scopeTags.map((tag) => (
                <label key={tag} className="morpheme-tooltip-scope-option">
                  <input
                    type="checkbox"
                    value={tag}
                    checked={selectedTags.includes(tag)}
                    disabled={isSaving || payload.requiredScopeTags.includes(tag)}
                    onClick={(event) => {
                      event.stopPropagation();
                    }}
                    onChange={(event) => {
                      if (payload.requiredScopeTags.includes(tag)) {
                        return;
                      }
                      const nextSelectedTags = event.target.checked
                        ? [...selectedTags, tag]
                        : selectedTags.filter((value) => value !== tag);
                      setSelectedTags(canonicalizeTooltipTags(nextSelectedTags));
                    }}
                  />
                  <span>{formatTooltipScopeTag(tag)}</span>
                </label>
              ))}
            </div>
            <textarea
              className="morpheme-tooltip-editor"
              rows={4}
              placeholder="Add a human note for this tag scope..."
              value={draftText}
              disabled={isSaving}
              onClick={(event) => {
                event.stopPropagation();
              }}
              onChange={(event) => {
                setDraftText(event.target.value);
              }}
            />
            <div className="morpheme-tooltip-status">{status}</div>
            <div className="morpheme-tooltip-actions">
              <button
                type="button"
                className="morpheme-tooltip-btn"
                disabled={isSaving}
                onClick={handleSave}
              >
                Save
              </button>
              <button
                type="button"
                className="morpheme-tooltip-btn ghost"
                disabled={isSaving}
                onClick={handleCancel}
              >
                Cancel
              </button>
            </div>
          </section>
        ) : (
          <>
            {payload.overrides.length ? (
              <section className="morpheme-tooltip-section">
                <div className="morpheme-tooltip-label">
                  {payload.overrides.length === 1 ? "Saved note" : "Saved notes"}
                </div>
                <div className="morpheme-tooltip-note-list">
                  {payload.overrides.map((note) => {
                    const scopeText = note.tags.map(formatTooltipScopeTag).join(" · ");
                    if (!tooltipEditingAvailable) {
                      return (
                        <div
                          key={note.tag_key}
                          className="morpheme-tooltip-note-card"
                          title={scopeText}
                        >
                          <div className="morpheme-tooltip-note">{note.text}</div>
                        </div>
                      );
                    }
                    return (
                      <button
                        key={note.tag_key}
                        type="button"
                        className="morpheme-tooltip-note-card"
                        title={scopeText}
                        onClick={(event) => {
                          handleStartEdit(event, note);
                        }}
                      >
                        <div className="morpheme-tooltip-note">{note.text}</div>
                      </button>
                    );
                  })}
                </div>
              </section>
            ) : null}

            {payload.tags.length ? (
              <section className="morpheme-tooltip-section">
                <div className="morpheme-tooltip-label">Tags</div>
                {payload.tags.map((tag) => (
                  <div key={tag} className="morpheme-tooltip-line">
                    {tag}
                  </div>
                ))}
              </section>
            ) : null}

            {payload.detailLines.length ? (
              <section className="morpheme-tooltip-section">
                <div className="morpheme-tooltip-label">Auto</div>
                {payload.detailLines.map((detailLine) => (
                  <div key={detailLine} className="morpheme-tooltip-line">
                    {detailLine}
                  </div>
                ))}
              </section>
            ) : null}

            {tooltipEditingAvailable && payload.tags.length ? (
              <div className="morpheme-tooltip-actions">
                <button
                  type="button"
                  className="morpheme-tooltip-btn"
                  onClick={(event) => {
                    handleStartEdit(event);
                  }}
                >
                  Add note
                </button>
              </div>
            ) : null}
          </>
        )}
      </span>
    </span>
  );
}

function spansOverlap(left, right) {
  return left.start <= right.end && right.start <= left.end;
}

function assignSyntaxRows(spans) {
  const rows = [];
  return [...spans]
    .sort((left, right) => {
      const leftWidth = left.end - left.start;
      const rightWidth = right.end - right.start;
      if (leftWidth !== rightWidth) {
        return leftWidth - rightWidth;
      }
      if ((right.depth || 0) !== (left.depth || 0)) {
        return (right.depth || 0) - (left.depth || 0);
      }
      if (left.start !== right.start) {
        return left.start - right.start;
      }
      return (left.node_id || 0) - (right.node_id || 0);
    })
    .map((span) => {
      const rowIndex = rows.findIndex((row) => (
        row.every((placedSpan) => !spansOverlap(placedSpan, span))
      ));
      const targetRow = rowIndex === -1 ? rows.length : rowIndex;
      if (!rows[targetRow]) {
        rows[targetRow] = [];
      }
      rows[targetRow].push(span);
      return { ...span, row: targetRow };
    });
}

function AnnotatedDisplay({
  contextId,
  lineOrAnnotatedText,
  entryPosHint,
  tooltipOverrides,
  tooltipEditingAvailable,
  navarroIndex,
  openTooltipId,
  setOpenTooltipId,
  onSaveTooltipOverride,
}) {
  const line =
    typeof lineOrAnnotatedText === "string"
      ? { annotated: lineOrAnnotatedText, morphemes: [] }
      : lineOrAnnotatedText || {};
  const annotatedText = line.annotated || "";
  const morphemeMetadata = Array.isArray(line.morphemes) ? line.morphemes : [];
  const inlineChildren = [];
  const displayItems = [];
  let morphemeIndex = 0;

  parseAnnotated(annotatedText).forEach(({ text, tags }, index) => {
    if (!tags.length) {
      if (text) {
        inlineChildren.push(
          <Fragment key={`${contextId}-text-${index}`}>
            {text}
          </Fragment>,
        );
        displayItems.push({
          key: `${contextId}-text-${index}`,
          type: "text",
          text,
          leadingSpace: "",
          morphemeIndex: null,
        });
      }
      return;
    }

    const morphemeMeta = morphemeMetadata[morphemeIndex] || null;
    const currentMorphemeIndex = morphemeIndex;
    morphemeIndex += 1;

    const leadingSpace = text.match(/^\s+/)?.[0] || "";
    const morpheme = text.slice(leadingSpace.length);
    if (leadingSpace) {
      inlineChildren.push(
        <Fragment key={`${contextId}-space-${index}`}>
          {leadingSpace}
        </Fragment>,
      );
    }
    if (!morpheme) {
      return;
    }

    const filteredTags = tags.filter((tag) => !/^deepest_node_/i.test(tag));
    const payload = buildTooltipPayload(
      filteredTags,
      morphemeMeta,
      morpheme,
      entryPosHint,
      tooltipOverrides,
      navarroIndex,
    );

    if (
      !filteredTags.length &&
      !payload.detailLines.length &&
      !payload.overrides.length
    ) {
      inlineChildren.push(
        <Fragment key={`${contextId}-plain-${index}`}>
          {morpheme}
        </Fragment>,
      );
      displayItems.push({
        key: `${contextId}-plain-${index}`,
        type: "text",
        text: morpheme,
        leadingSpace,
        morphemeIndex: currentMorphemeIndex,
      });
      return;
    }

    const chunk = (
      <MorphemeChunk
        key={`${contextId}-morpheme-${index}`}
        chunkId={`${contextId}-morpheme-${index}`}
        morpheme={morpheme}
        payload={payload}
        openTooltipId={openTooltipId}
        setOpenTooltipId={setOpenTooltipId}
        tooltipEditingAvailable={tooltipEditingAvailable}
        onSaveTooltipOverride={onSaveTooltipOverride}
      />
    );
    inlineChildren.push(chunk);
    displayItems.push({
      key: `${contextId}-morpheme-cell-${index}`,
      type: "morpheme",
      content: chunk,
      leadingSpace,
      morphemeIndex: currentMorphemeIndex,
    });
  });

  const morphemeColumns = new Map();
  displayItems.forEach((item, itemIndex) => {
    if (item.morphemeIndex !== null) {
      morphemeColumns.set(item.morphemeIndex, itemIndex + 1);
    }
  });

  const syntaxSpans = assignSyntaxRows(
    (Array.isArray(line.syntax_spans) ? line.syntax_spans : [])
      .map((span) => ({
        ...span,
        start: Number(span.start),
        end: Number(span.end),
      }))
      .filter((span) => (
        Number.isInteger(span.start) &&
        Number.isInteger(span.end) &&
        span.end > span.start &&
        morphemeColumns.has(span.start) &&
        morphemeColumns.has(span.end)
      )),
  );

  if (!syntaxSpans.length) {
    return <p className="annotated-display">{inlineChildren}</p>;
  }

  return (
    <p className="annotated-display syntax-display">
      {displayItems.map((item, itemIndex) => {
        const gridColumn = itemIndex + 1;
        const leadingSpaceWidth = item.leadingSpace
          ? `${Math.min(item.leadingSpace.length, 4) * 0.35}rem`
          : "0";
        return (
          <span
            key={item.key}
            className={
              item.type === "morpheme"
                ? "syntax-display-cell"
                : "syntax-display-cell syntax-display-text"
            }
            style={{
              gridColumn,
              gridRow: 1,
              "--syntax-leading-space": leadingSpaceWidth,
            }}
          >
            {item.content || item.text}
          </span>
        );
      })}
      {syntaxSpans.map((span, index) => {
        const color = tagToColors(
          `syntax-${span.label || span.kind || span.node_id}-${span.depth || 0}`,
        ).color;
        const startColumn = morphemeColumns.get(span.start);
        const endColumn = morphemeColumns.get(span.end) + 1;
        return (
          <span
            key={`${contextId}-syntax-span-${span.node_id}-${span.start}-${span.end}-${index}`}
            className="syntax-span"
            aria-hidden="true"
            title={span.label || ""}
            style={{
              gridColumn: `${startColumn} / ${endColumn}`,
              gridRow: span.row + 2,
              "--syntax-color": color,
            }}
          />
        );
      })}
    </p>
  );
}

function EntryCard({
  result,
  lineLookup,
  tooltipOverrides,
  tooltipEditingAvailable,
  navarroIndex,
  openTooltipId,
  setOpenTooltipId,
  onSaveTooltipOverride,
}) {
  const { entry, score } = result;
  const definition = entry.definition || { qualifiers: [], glosses: [], raw: "" };

  return (
    <article className="entry-card">
      <div className="entry-top">
        <div className="entry-heading">
          <h2>{entry.headword}</h2>
        </div>

        <div className="entry-badges">
          {makeChip(
            entry.dataset === "lexicon" ? "Lexicon" : "Navarro supplement",
            "badge",
          )}
          {entry.part_of_speech?.kind
            ? makeChip(entry.part_of_speech.kind, "badge")
            : null}
          {entry.metadata?.definition_missing
            ? makeChip("Gloss pending", "badge")
            : null}
          {result.match
            ? makeChip(
                `${result.match.fieldLabel}: ${QUALITY_LABELS[result.match.quality]}`,
                "badge metric",
              )
            : null}
          {score !== null && score <= 1 ? makeChip("Exact match", "badge exact") : null}
        </div>
      </div>

      <div className="entry-body">
        <section>
          {definition.qualifiers?.length ? (
            <>
              <span className="field-label">Qualifiers</span>
              <div className="entry-tags">
                {definition.qualifiers.map((qualifier) => (
                  <span key={qualifier} className="tag">
                    {qualifier}
                  </span>
                ))}
              </div>
            </>
          ) : null}

          <span className="field-label">Glosses</span>
          <div className="gloss-list">
            {(definition.glosses || []).length ? (
              definition.glosses.map((gloss) => (
                <span key={gloss} className="gloss">
                  {gloss}
                </span>
              ))
            ) : (
              <span className="gloss">Definition pending</span>
            )}
          </div>
        </section>

        {result.match ? (
          <section>
            <span className="field-label">Matched</span>
            <div className="aliases">
              {result.match.fieldLabel} · {QUALITY_LABELS[result.match.quality]}
              {result.match.preview && result.match.preview !== entry.headword
                ? ` · ${result.match.preview}`
                : ""}
            </div>
          </section>
        ) : null}

        {entry.aliases?.length ? (
          <section>
            <span className="field-label">Aliases</span>
            <div className="aliases">{entry.aliases.join(", ")}</div>
          </section>
        ) : null}

        {entry.source_counts?.length ? (
          <section>
            <span className="field-label">Sources</span>
            <div className="source-chips">
              {entry.source_counts.map((item) => (
                <span
                  key={`${item.source}-${item.count}`}
                  className="source-chip"
                >
                  {item.source} ({item.count})
                </span>
              ))}
            </div>
          </section>
        ) : null}

        {entry.attestations?.length ? (
          <section className="attestations">
            <details defaultOpen={entry.attestation_count <= 3}>
              <summary>Attestations ({entry.attestation_count})</summary>
              <div className="attestation-list">
                {entry.attestations.map((attestation) => {
                  const line = lineLookup.get(attestation.line_id);
                  if (!line) {
                    return null;
                  }

                  return (
                    <article key={attestation.line_id} className="attestation-card">
                      <div className="source-chips">
                        <span className="source-chip">
                          {line.source}:{line.expression_index}
                        </span>
                      </div>
                      <p className="attestation-surface">{line.surface}</p>
                      <AnnotatedDisplay
                        contextId={attestation.line_id}
                        lineOrAnnotatedText={line}
                        entryPosHint={entry.part_of_speech?.kind || ""}
                        tooltipOverrides={tooltipOverrides}
                        tooltipEditingAvailable={tooltipEditingAvailable}
                        navarroIndex={navarroIndex}
                        openTooltipId={openTooltipId}
                        setOpenTooltipId={setOpenTooltipId}
                        onSaveTooltipOverride={onSaveTooltipOverride}
                      />
                    </article>
                  );
                })}
              </div>
            </details>
          </section>
        ) : null}
      </div>
    </article>
  );
}

function CorpusNav({ index, total, onPrevious, onNext, position = "top" }) {
  return (
    <div className={position === "bottom" ? "corpus-nav corpus-nav-bottom" : "corpus-nav"}>
      <button
        type="button"
        className="corpus-nav-btn"
        disabled={index === 0}
        onClick={onPrevious}
      >
        ← Prev
      </button>
      <span className="corpus-nav-counter">
        {index + 1} / {total}
      </span>
      <button
        type="button"
        className="corpus-nav-btn"
        disabled={index === total - 1}
        onClick={onNext}
      >
        Next →
      </button>
    </div>
  );
}

export default function App() {
  const [queryInput, setQueryInput] = useState(INITIAL_URL_STATE.query);
  const [query, setQuery] = useState(INITIAL_URL_STATE.query);
  const [settings, setSettings] = useState({
    metric: INITIAL_URL_STATE.metric,
    sort: INITIAL_URL_STATE.sort,
    direction: INITIAL_URL_STATE.direction,
  });
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [dictionaryEntries, setDictionaryEntries] = useState([]);
  const [dictionaryMeta, setDictionaryMeta] = useState({});
  const [renderedCorpus, setRenderedCorpus] = useState(null);
  const [corpusMeta, setCorpusMeta] = useState({});
  const [lineLookup, setLineLookup] = useState(new Map());
  const [searchDocuments, setSearchDocuments] = useState([]);
  const [navarroIndex, setNavarroIndex] = useState(null);
  const [tooltipOverrides, setTooltipOverrides] = useState([]);
  const [tooltipEditingAvailable, setTooltipEditingAvailable] = useState(false);
  const [activeTab, setActiveTab] = useState("dictionary");
  const [activeCorpusSource, setActiveCorpusSource] = useState("");
  const [corpusLineIndex, setCorpusLineIndex] = useState(0);
  const [selectedKinds, setSelectedKinds] = useState([]);
  const [posFilterInitialized, setPosFilterInitialized] = useState(false);
  const [openTooltipId, setOpenTooltipId] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const [entryPayload, corpusPayload, navarroPayload, tooltipOverridePayload] =
          await Promise.all([
            fetchMaybeGzipJson(ENTRY_PATH),
            fetchMaybeGzipJson(CORPUS_PATH),
            fetchMaybeGzipJson(NAVARRO_PATH).catch(() => null),
            fetchTooltipOverrides().catch(() => null),
          ]);

        if (cancelled) {
          return;
        }

        const entries = entryPayload.entries || [];
        const nextLineLookup = buildLineLookup(corpusPayload);
        setDictionaryEntries(entries);
        setDictionaryMeta(entryPayload.meta || {});
        setRenderedCorpus(corpusPayload);
        setCorpusMeta(corpusPayload.meta || {});
        setLineLookup(nextLineLookup);
        setSearchDocuments(buildSearchDocuments(entries, nextLineLookup));
        setNavarroIndex(Array.isArray(navarroPayload) ? buildNavarroIndex(navarroPayload) : null);
        setTooltipOverrides(
          Array.isArray(tooltipOverridePayload?.entries)
            ? tooltipOverridePayload.entries.map((entry) =>
                normalizeTooltipOverrideEntry(entry),
              )
            : [],
        );
        setTooltipEditingAvailable(Boolean(tooltipOverridePayload));
        setLoading(false);
      } catch (error) {
        if (cancelled) {
          return;
        }
        console.error(error);
        setLoadError("Failed to load dictionary artifacts.");
        setLoading(false);
      }
    }

    bootstrap();
    return () => {
      cancelled = true;
    };
  }, []);

  const kindCounts = dictionaryEntries.reduce((counts, entry) => {
    const kind = entry.part_of_speech?.kind || "(unknown)";
    counts.set(kind, (counts.get(kind) || 0) + 1);
    return counts;
  }, new Map());

  const sortedKinds = Array.from(kindCounts.keys()).sort((left, right) => {
    const countDelta = (kindCounts.get(right) || 0) - (kindCounts.get(left) || 0);
    return countDelta !== 0 ? countDelta : left.localeCompare(right);
  });

  useEffect(() => {
    if (!posFilterInitialized && sortedKinds.length) {
      setSelectedKinds(sortedKinds);
      setPosFilterInitialized(true);
    }
  }, [posFilterInitialized, sortedKinds]);

  const sourceEntries = Object.entries(renderedCorpus?.sources || {});

  useEffect(() => {
    if (!sourceEntries.length) {
      return;
    }
    if (!activeCorpusSource || !renderedCorpus?.sources?.[activeCorpusSource]) {
      setActiveCorpusSource(sourceEntries[0][0]);
      setCorpusLineIndex(0);
    }
  }, [activeCorpusSource, renderedCorpus, sourceEntries]);

  useEffect(() => {
    const handleDocumentClick = () => {
      setOpenTooltipId(null);
    };
    const handleDocumentKeyDown = (event) => {
      if (event.key === "Escape") {
        setOpenTooltipId(null);
      }
    };

    document.addEventListener("click", handleDocumentClick);
    document.addEventListener("keydown", handleDocumentKeyDown);
    return () => {
      document.removeEventListener("click", handleDocumentClick);
      document.removeEventListener("keydown", handleDocumentKeyDown);
    };
  }, []);

  useEffect(() => {
    const handlePopState = () => {
      const nextState = readSettingsFromUrl();
      setQueryInput(nextState.query);
      setQuery(nextState.query);
      setSettings({
        metric: nextState.metric,
        sort: nextState.sort,
        direction: nextState.direction,
      });
    };

    window.addEventListener("popstate", handlePopState);
    return () => {
      window.removeEventListener("popstate", handlePopState);
    };
  }, []);

  useEffect(() => {
    if (activeTab !== "corpus") {
      return undefined;
    }

    const handleCorpusNavigation = (event) => {
      const activeTagName = document.activeElement?.tagName;
      if (activeTagName === "INPUT" || activeTagName === "TEXTAREA" || activeTagName === "SELECT") {
        return;
      }

      const lines = renderedCorpus?.sources?.[activeCorpusSource]?.lines || [];
      if (!lines.length) {
        return;
      }

      if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
        event.preventDefault();
        setCorpusLineIndex((currentIndex) => Math.max(0, currentIndex - 1));
      } else if (event.key === "ArrowRight" || event.key === "ArrowDown") {
        event.preventDefault();
        setCorpusLineIndex((currentIndex) => Math.min(lines.length - 1, currentIndex + 1));
      }
    };

    document.addEventListener("keydown", handleCorpusNavigation);
    return () => {
      document.removeEventListener("keydown", handleCorpusNavigation);
    };
  }, [activeCorpusSource, activeTab, renderedCorpus]);

  useEffect(() => {
    setOpenTooltipId(null);
  }, [
    query,
    settings.metric,
    settings.sort,
    settings.direction,
    selectedKinds.join("|"),
    activeTab,
    activeCorpusSource,
    corpusLineIndex,
    tooltipOverrides,
  ]);

  const applySearchState = (nextQuery, nextSettings, { push = true } = {}) => {
    const compactQuery = compactWhitespace(nextQuery);
    setQueryInput(compactQuery);
    setQuery(compactQuery);
    setSettings(nextSettings);
    syncQuery(compactQuery, nextSettings, { push });
  };

  const activePosFilter =
    posFilterInitialized && sortedKinds.length && selectedKinds.length !== sortedKinds.length
      ? new Set(selectedKinds)
      : null;

  let resultSet = [];
  let summaryText = "Loading dictionary artifacts...";

  if (loadError) {
    summaryText = "Dictionary artifacts could not be loaded.";
  } else if (!loading && renderedCorpus) {
    if (!query) {
      const displaySort = settings.sort === "best_match" ? "attestation_count" : settings.sort;
      const displayDirection =
        settings.sort === "best_match"
          ? defaultDirectionFor(displaySort)
          : settings.direction;
      resultSet = topEntries(settings, dictionaryEntries, activePosFilter);
      summaryText =
        `Loaded ${dictionaryEntries.length} structured entries and ${renderedCorpus.meta.line_count} rendered corpus lines. ` +
        `Showing attested lexicon entries sorted by ${getSortLabel(displaySort)} (${getDirectionLabel(displayDirection)}).`;
    } else {
      resultSet = searchEntries(query, settings, searchDocuments, activePosFilter);
      summaryText =
        `Found ${resultSet.length} result${resultSet.length === 1 ? "" : "s"} for "${query}" ` +
        `using ${getMetricLabel(settings.metric)}, sorted by ${getSortLabel(settings.sort)} (${getDirectionLabel(settings.direction)}).`;
    }
  }

  const currentSourceData = renderedCorpus?.sources?.[activeCorpusSource];
  const currentSourceLines = currentSourceData?.lines || [];
  const currentCorpusIndex = currentSourceLines.length
    ? Math.max(0, Math.min(corpusLineIndex, currentSourceLines.length - 1))
    : 0;
  const currentCorpusLine = currentSourceLines[currentCorpusIndex] || null;

  const handleSaveTooltipOverride = async (tags, text) => {
    const result = await saveTooltipOverrideRequest(tags, text);
    setTooltipOverrides((currentOverrides) => {
      if (result.deleted) {
        return removeTooltipOverrideEntry(currentOverrides, tags);
      }
      if (result.entry) {
        return replaceTooltipOverrideEntry(currentOverrides, result.entry);
      }
      return currentOverrides;
    });
    return result;
  };

  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">Old Tupi Corpus</p>
        <h1>Static Dictionary v1</h1>
        <p className="lede">
          Search structured lexicon entries built from the historic source-of-truth
          corpus, with line-level attestations linked back to rendered corpus records.
        </p>
        <form
          className="search-panel"
          onSubmit={(event) => {
            event.preventDefault();
            applySearchState(queryInput, settings);
          }}
        >
          <label className="sr-only" htmlFor="search-input">
            Search dictionary
          </label>
          <input
            id="search-input"
            name="query"
            type="search"
            placeholder="Search headword, alias, gloss, or attested surface"
            autoComplete="off"
            spellCheck="false"
            value={queryInput}
            onChange={(event) => {
              setQueryInput(event.target.value);
            }}
          />
          <button type="submit">Search</button>
        </form>
        <div className="search-toolbar">
          <label className="control">
            <span>Metric</span>
            <select
              value={settings.metric}
              onChange={(event) => {
                const nextMetric = isValidKey(event.target.value, METRIC_OPTIONS)
                  ? event.target.value
                  : "smart";
                applySearchState(queryInput, {
                  ...settings,
                  metric: nextMetric,
                });
              }}
            >
              {Object.entries(METRIC_OPTIONS).map(([key, option]) => (
                <option key={key} value={key}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="control">
            <span>Sort</span>
            <select
              value={settings.sort}
              onChange={(event) => {
                const nextSort = isValidKey(event.target.value, SORT_OPTIONS)
                  ? event.target.value
                  : "best_match";
                applySearchState(queryInput, {
                  ...settings,
                  sort: nextSort,
                  direction: defaultDirectionFor(nextSort),
                });
              }}
            >
              {Object.entries(SORT_OPTIONS).map(([key, option]) => (
                <option key={key} value={key}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label className="control">
            <span>Direction</span>
            <select
              value={settings.direction}
              onChange={(event) => {
                applySearchState(queryInput, {
                  ...settings,
                  direction: event.target.value === "desc" ? "desc" : "asc",
                });
              }}
            >
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
          </label>
        </div>
        <div className="status-row">
          <div className="summary">{summaryText}</div>
          <button
            className="ghost"
            type="button"
            onClick={() => {
              applySearchState("", settings);
            }}
          >
            Clear
          </button>
        </div>
      </section>

      <nav className="tab-nav">
        <button
          type="button"
          className={`tab-btn${activeTab === "dictionary" ? " active" : ""}`}
          onClick={() => {
            setActiveTab("dictionary");
          }}
        >
          Dictionary
        </button>
        <button
          type="button"
          className={`tab-btn${activeTab === "corpus" ? " active" : ""}`}
          onClick={() => {
            setActiveTab("corpus");
          }}
        >
          Corpus
        </button>
      </nav>

      <div className={`tab-panel${activeTab === "dictionary" ? "" : " hidden"}`}>
        <section className="layout">
          <aside className="sidebar">
            <div className="panel">
              <h2>Build</h2>
              <dl className="meta-list">
                <div>
                  <dt>Entries</dt>
                  <dd>{dictionaryMeta.entry_count || "-"}</dd>
                </div>
                <div>
                  <dt>Corpus lines</dt>
                  <dd>{corpusMeta.line_count || "-"}</dd>
                </div>
                <div>
                  <dt>Historic sources</dt>
                  <dd>{corpusMeta.source_count || "-"}</dd>
                </div>
                <div>
                  <dt>Generated</dt>
                  <dd>{compactWhitespace(dictionaryMeta.generated_at || corpusMeta.generated_at || "-")}</dd>
                </div>
              </dl>
            </div>

            <div className="panel">
              <h2>Filter</h2>
              <div>
                <div className="filter-group-header">
                  <span className="filter-group-label">Part of Speech</span>
                  <div className="filter-btn-row">
                    <button
                      type="button"
                      className="filter-toggle-btn"
                      onClick={() => {
                        setSelectedKinds(sortedKinds);
                        setPosFilterInitialized(true);
                      }}
                    >
                      All
                    </button>
                    <button
                      type="button"
                      className="filter-toggle-btn"
                      onClick={() => {
                        setSelectedKinds([]);
                        setPosFilterInitialized(true);
                      }}
                    >
                      None
                    </button>
                  </div>
                </div>

                {sortedKinds.map((kind) => (
                  <label key={kind} className="filter-check-row">
                    <input
                      type="checkbox"
                      value={kind}
                      checked={!posFilterInitialized || selectedKinds.includes(kind)}
                      onChange={(event) => {
                        setPosFilterInitialized(true);
                        setSelectedKinds((currentKinds) => {
                          if (event.target.checked) {
                            return [...currentKinds, kind].sort((left, right) =>
                              left.localeCompare(right),
                            );
                          }
                          return currentKinds.filter((value) => value !== kind);
                        });
                      }}
                    />
                    <span className="filter-check-label">{kind}</span>
                    <span className="filter-check-count">{kindCounts.get(kind) || 0}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="panel">
              <h2>Search notes</h2>
              <ul className="notes">
                <li>`Smart` combines headword, alias, gloss, attestation, source, and full-text matches.</li>
                <li>Use `Metric` to search one field family only.</li>
                <li>`Best Match`, alphabetical, and count-based sorts all support ascending and descending order.</li>
                <li>Attestations come from `historic/*.tu.py` renderings.</li>
                <li>Tooltip notes can be edited locally and persist in SQLite when served with `make serve-dict`.</li>
              </ul>
            </div>
          </aside>

          <section className="results-panel">
            <div className="results" aria-live="polite">
              {loadError ? (
                <div className="error-state">{loadError}</div>
              ) : loading ? (
                <div className="empty-state">Loading dictionary artifacts...</div>
              ) : resultSet.length ? (
                resultSet.map((result) => (
                  <EntryCard
                    key={result.entry.entry_id}
                    result={result}
                    lineLookup={lineLookup}
                    tooltipOverrides={tooltipOverrides}
                    tooltipEditingAvailable={tooltipEditingAvailable}
                    navarroIndex={navarroIndex}
                    openTooltipId={openTooltipId}
                    setOpenTooltipId={setOpenTooltipId}
                    onSaveTooltipOverride={handleSaveTooltipOverride}
                  />
                ))
              ) : (
                <div className="empty-state">
                  No results found for that query.
                </div>
              )}
            </div>
          </section>
        </section>
      </div>

      <div className={`tab-panel${activeTab === "corpus" ? "" : " hidden"}`}>
        <section className="layout">
          <aside className="sidebar">
            <div className="panel">
              <h2>Works</h2>
              <div>
                {sourceEntries.length ? (
                  sourceEntries.map(([sourceName, sourceData]) => (
                    <button
                      key={sourceName}
                      type="button"
                      className={`corpus-source-btn${activeCorpusSource === sourceName ? " active" : ""}`}
                      onClick={() => {
                        setActiveCorpusSource(sourceName);
                        setCorpusLineIndex(0);
                      }}
                    >
                      <span>{sourceName}</span>
                      <span className="corpus-source-count">
                        {sourceData.line_count || 0}
                      </span>
                    </button>
                  ))
                ) : (
                  <div className="empty-state">No corpus sources loaded.</div>
                )}
              </div>
            </div>
          </aside>

          <section className="results-panel">
            <div className="corpus-viewer">
              {currentCorpusLine ? (
                <>
                  <div className="corpus-header">
                    <h2 className="corpus-title">{activeCorpusSource}</h2>
                  </div>
                  <CorpusNav
                    index={currentCorpusIndex}
                    total={currentSourceLines.length}
                    onPrevious={() => {
                      setCorpusLineIndex((index) => Math.max(0, index - 1));
                    }}
                    onNext={() => {
                      setCorpusLineIndex((index) =>
                        Math.min(currentSourceLines.length - 1, index + 1),
                      );
                    }}
                  />
                  <article className="corpus-line-card">
                    <p className="corpus-surface">{currentCorpusLine.surface}</p>
                    <AnnotatedDisplay
                      contextId={currentCorpusLine.line_id}
                      lineOrAnnotatedText={currentCorpusLine}
                      entryPosHint=""
                      tooltipOverrides={tooltipOverrides}
                      tooltipEditingAvailable={tooltipEditingAvailable}
                      navarroIndex={navarroIndex}
                      openTooltipId={openTooltipId}
                      setOpenTooltipId={setOpenTooltipId}
                      onSaveTooltipOverride={handleSaveTooltipOverride}
                    />
                  </article>
                  <CorpusNav
                    index={currentCorpusIndex}
                    total={currentSourceLines.length}
                    position="bottom"
                    onPrevious={() => {
                      setCorpusLineIndex((index) => Math.max(0, index - 1));
                    }}
                    onNext={() => {
                      setCorpusLineIndex((index) =>
                        Math.min(currentSourceLines.length - 1, index + 1),
                      );
                    }}
                  />
                </>
              ) : (
                <div className="empty-state">No lines in this source.</div>
              )}
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}
