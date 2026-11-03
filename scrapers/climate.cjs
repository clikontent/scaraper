const fetch = require("node-fetch");
const { createClient } = require("@supabase/supabase-js");
const { shouldKeepJob } = require("./filters.cjs");
require("dotenv").config();

// ============================================================
// SUPABASE
// ============================================================

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_ROLE_KEY
);

// ============================================================
// CONFIG
// ============================================================

const BASE_URL =
  "https://www.climatechangecareers.com";

const REMOTE_JOBS_URL =
  `${BASE_URL}/jobs/?remote=remote`;

const MAX_PAGES =
  Number(process.env.CLIMATE_CHANGE_CAREERS_MAX_PAGES || 5);

const CHUNK_SIZE = 50;

const USER_AGENT =
  process.env.CLIMATE_CHANGE_CAREERS_USER_AGENT ||
  "KaziNest Job Aggregator/1.0";

// ============================================================
// HELPERS
// ============================================================

function cleanText(value = "") {
  return String(value)
    .replace(/\s+/g, " ")
    .trim();
}

function absoluteUrl(url) {
  if (!url) {
    return "";
  }

  try {
    return new URL(url, BASE_URL).href;
  } catch {
    return "";
  }
}

function stripHtml(html = "") {
  return String(html)
    .replace(
      /<script[\s\S]*?<\/script>/gi,
      " "
    )
    .replace(
      /<style[\s\S]*?<\/style>/gi,
      " "
    )
    .replace(
      /<\/?(p|div|section|article|li|ul|ol|br|h1|h2|h3|h4|h5|h6)[^>]*>/gi,
      "\n"
    )
    .replace(
      /<[^>]+>/g,
      " "
    )
    .replace(
      /&nbsp;/gi,
      " "
    )
    .replace(
      /&amp;/gi,
      "&"
    )
    .replace(
      /&quot;/gi,
      '"'
    )
    .replace(
      /&#39;/gi,
      "'"
    )
    .replace(
      /&apos;/gi,
      "'"
    )
    .replace(
      /&lt;/gi,
      "<"
    )
    .replace(
      /&gt;/gi,
      ">"
    )
    .replace(
      /\s+\n/g,
      "\n"
    )
    .replace(
      /\n\s+/g,
      "\n"
    )
    .replace(
      /\n{3,}/g,
      "\n\n"
    )
    .replace(
      /[ \t]+/g,
      " "
    )
    .trim();
}

// ============================================================
// HTML SELECTOR HELPER
// ============================================================
//
// We don't use a DOM dependency here so the scraper remains
// lightweight. These helpers use the HTML structure directly.
//
// If the site's markup changes, the selectors can be updated
// without touching the Supabase/filtering pipeline.
// ============================================================

function extractAttribute(
  html,
  tag,
  attribute
) {
  const regex = new RegExp(
    `<${tag}\\b[^>]*\\b${attribute}=["']([^"']+)["'][^>]*>`,
    "i"
  );

  const match =
    html.match(regex);

  return match
    ? cleanText(match[1])
    : "";
}

function extractTextByClass(
  html,
  className
) {
  const escaped =
    className.replace(
      /[.*+?^${}()|[\]\\]/g,
      "\\$&"
    );

  const regex =
    new RegExp(
      `<[^>]*class=["'][^"']*\\b${escaped}\\b[^"']*["'][^>]*>([\\s\\S]*?)<\\/[^>]+>`,
      "i"
    );

  const match =
    html.match(regex);

  return match
    ? cleanText(
        stripHtml(match[1])
      )
    : "";
}

function extractFirstHeading(
  html
) {
  const match =
    html.match(
      /<h[1-3]\b[^>]*>([\s\S]*?)<\/h[1-3]>/i
    );

  return match
    ? cleanText(
        stripHtml(match[1])
      )
    : "";
}

// ============================================================
// FETCH PAGE
// ============================================================

async function fetchPage(url) {
  console.log(`📡 Fetching: ${url}`);

  const response =
    await fetch(
      url,
      {
        method: "GET",

        headers: {
          "User-Agent":
            USER_AGENT,

          Accept:
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",

          "Cache-Control":
            "no-cache",
        },

        timeout: 30000,
      }
    );

  if (!response.ok) {
    throw new Error(
      `HTTP ${response.status} ${response.statusText}`
    );
  }

  return response.text();
}

// ============================================================
// FIND JOB CARDS
// ============================================================
//
// ClimateChangeCareers currently exposes job listings using
// job-card style elements.
//
// We first identify the complete card and then extract fields
// from inside it.
// ============================================================

function extractJobCards(html) {
  const cards = [];

  const patterns = [
    /<div\b[^>]*class=["'][^"']*\bjob-card\b[^"']*["'][^>]*>[\s\S]*?<\/div>/gi,

    /<li\b[^>]*class=["'][^"']*\bjob-card\b[^"']*["'][^>]*>[\s\S]*?<\/li>/gi,

    /<article\b[^>]*class=["'][^"']*\bjob-card\b[^"']*["'][^>]*>[\s\S]*?<\/article>/gi,
  ];

  for (
    const pattern of patterns
  ) {
    const matches =
      html.match(pattern);

    if (
      matches &&
      matches.length
    ) {
      cards.push(
        ...matches
      );
    }
  }

  // Deduplicate cards.
  return Array.from(
    new Set(cards)
  );
}

// ============================================================
// EXTRACT JOB FROM CARD
// ============================================================

function parseJobCard(
  card,
  pageUrl
) {
  try {
    // --------------------------------------------------------
    // TITLE + LINK
    // --------------------------------------------------------

    const titleMatch =
      card.match(
        /<h[2-4]\b[^>]*>[\s\S]*?<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>[\s\S]*?<\/h[2-4]>/i
      );

    let title = "";
    let link = "";

    if (titleMatch) {
      link =
        absoluteUrl(
          titleMatch[1]
        );

      title =
        cleanText(
          stripHtml(
            titleMatch[2]
          )
        );
    }

    // Fallback: first useful anchor.
    if (!link) {
      const anchorMatch =
        card.match(
          /<a\b[^>]*href=["']([^"']+)["'][^>]*>([\s\S]*?)<\/a>/i
        );

      if (anchorMatch) {
        link =
          absoluteUrl(
            anchorMatch[1]
          );

        if (!title) {
          title =
            cleanText(
              stripHtml(
                anchorMatch[2]
              )
            );
        }
      }
    }

    // --------------------------------------------------------
    // COMPANY
    // --------------------------------------------------------

    const company =
      extractTextByClass(
        card,
        "company"
      ) ||
      extractTextByClass(
        card,
        "job-company"
      ) ||
      extractTextByClass(
        card,
        "employer"
      ) ||
      "Unknown";

    // --------------------------------------------------------
    // LOCATION
    // --------------------------------------------------------

    const location =
      extractTextByClass(
        card,
        "location"
      ) ||
      extractTextByClass(
        card,
        "job-location"
      ) ||
      "Remote";

    // --------------------------------------------------------
    // CATEGORY
    // --------------------------------------------------------

    const category =
      extractTextByClass(
        card,
        "category"
      ) ||
      extractTextByClass(
        card,
        "job-category"
      ) ||
      null;

    if (
      !title ||
      !link
    ) {
      return null;
    }

    // --------------------------------------------------------
    // RETURN
    // --------------------------------------------------------

    return {
      external_id:
        link,

      title,

      company,

      description:
        null,

      location,

      job_type:
        null,

      salary:
        null,

      experience_level:
        null,

      skills:
        [],

      requirements:
        [],

      // The listing page does not reliably expose
      // a publication timestamp.
      posted_date:
        new Date().toISOString(),

      expiry_date:
        null,

      application_url:
        link,

      company_logo:
        null,

      source:
        "ClimateChangeCareers",

      category,

      raw_data:
        card,

      country:
        null,

      metadata:
        JSON.stringify({
          listing_page:
            pageUrl,
        }),

      scraped_at:
        new Date().toISOString(),

      url:
        link,

      is_remote:
        true,

      slug:
        link,
    };
  } catch (error) {
    console.error(
      "ClimateChangeCareers card error:",
      error?.message ||
        error
    );

    return null;
  }
}

// ============================================================
// OPTIONAL DETAIL PAGE
// ============================================================
//
// Fetch additional information from the individual job page.
//
// This is intentionally conservative. If a selector isn't
// available, the existing value is preserved.
// ============================================================

async function enrichJob(
  job
) {
  if (
    !job?.application_url
  ) {
    return job;
  }

  try {
    const html =
      await fetchPage(
        job.application_url
      );

    // --------------------------------------------------------
    // DESCRIPTION
    // --------------------------------------------------------

    const descriptionCandidates = [
      extractTextByClass(
        html,
        "job-description"
      ),

      extractTextByClass(
        html,
        "job-content"
      ),

      extractTextByClass(
        html,
        "description"
      ),

      extractTextByClass(
        html,
        "job-details"
      ),
    ];

    const description =
      descriptionCandidates.find(
        Boolean
      );

    if (
      description &&
      description.length > 100
    ) {
      job.description =
        description;
    }

    // --------------------------------------------------------
    // COMPANY
    // --------------------------------------------------------

    const company =
      extractTextByClass(
        html,
        "company"
      ) ||
      extractTextByClass(
        html,
        "job-company"
      );

    if (
      company
    ) {
      job.company =
        company;
    }

    // --------------------------------------------------------
    // LOCATION
    // --------------------------------------------------------

    const location =
      extractTextByClass(
        html,
        "location"
      ) ||
      extractTextByClass(
        html,
        "job-location"
      );

    if (
      location
    ) {
      job.location =
        location;
    }

    // --------------------------------------------------------
    // JOB TYPE
    // --------------------------------------------------------

    const jobType =
      extractTextByClass(
        html,
        "job-type"
      );

    if (
      jobType
    ) {
      job.job_type =
        jobType;
    }

    // --------------------------------------------------------
    // SALARY
    // --------------------------------------------------------

    const salary =
      extractTextByClass(
        html,
        "salary"
      );

    if (
      salary
    ) {
      job.salary =
        salary;
    }

    // --------------------------------------------------------
    // RAW DATA
    // --------------------------------------------------------

    job.raw_data =
      html;

    return job;
  } catch (error) {
    // Detail enrichment should NEVER kill the scraper.
    console.warn(
      `⚠️ Could not enrich "${job.title}":`,
      error?.message ||
        error
    );

    return job;
  }
}

// ============================================================
// MAIN SCRAPER
// ============================================================

async function run() {
  console.log("");
  console.log(
    "=================================================="
  );
  console.log(
    "🚀 KaziNest - ClimateChangeCareers Scraper"
  );
  console.log(
    "=================================================="
  );

  console.log(
    `📚 Maximum pages: ${MAX_PAGES}`
  );

  const allJobs = [];

  // ==========================================================
  // 1. SCRAPE LISTING PAGES
  // ==========================================================

  for (
    let page = 1;
    page <= MAX_PAGES;
    page++
  ) {
    const url =
      `${REMOTE_JOBS_URL}&page=${page}`;

    try {
      const html =
        await fetchPage(url);

      const cards =
        extractJobCards(
          html
        );

      console.log(
        `   📄 Page ${page}: ${cards.length} job cards`
      );

      if (
        cards.length === 0
      ) {
        console.log(
          `   ⚠️ No jobs found on page ${page}. Stopping.`
        );

        break;
      }

      for (
        const card of cards
      ) {
        const job =
          parseJobCard(
            card,
            url
          );

        if (
          job
        ) {
          allJobs.push(
            job
          );
        }
      }
    } catch (error) {
      console.error(
        `❌ Page ${page} failed:`,
        error?.message ||
          error
      );
    }
  }

  console.log("");
  console.log(
    `📦 Raw scraped jobs: ${allJobs.length}`
  );

  // ==========================================================
  // 2. DEDUPLICATE
  // ==========================================================

  const uniqueJobs =
    Array.from(
      new Map(
        allJobs.map(
          (job) => [
            job.external_id,
            job,
          ]
        )
      ).values()
    );

  console.log(
    `🔑 Unique jobs: ${uniqueJobs.length}`
  );

  // ==========================================================
  // 3. ENRICH DETAIL PAGES
  // ==========================================================

  console.log("");
  console.log(
    "🔎 Enriching job detail pages..."
  );

  const enrichedJobs =
    [];

  for (
    const job of uniqueJobs
  ) {
    const enriched =
      await enrichJob(
        job
      );

    enrichedJobs.push(
      enriched
    );
  }

  console.log(
    `📝 Enriched jobs: ${enrichedJobs.length}`
  );

  // ==========================================================
  // 4. KAZINEST AFRICA/REMOTE FILTER
  // ==========================================================

  const filteredJobs =
    [];

  let rejectedCount =
    0;

  for (
    const job of enrichedJobs
  ) {
    try {
      const keep =
        shouldKeepJob({
          title:
            job.title,

          location:
            job.location ||
            "Remote",

          remote:
            true,

          description:
            job.description ||
            "",

          company:
            job.company ||
            "",

          category:
            job.category ||
            "",
        });

      if (
        keep
      ) {
        filteredJobs.push(
          job
        );
      } else {
        rejectedCount++;

        console.log(
          `🚫 Rejected: ${job.title} — ${job.location}`
        );
      }
    } catch (error) {
      console.error(
        `⚠️ Filter error for "${job.title}":`,
        error?.message ||
          error
      );
    }
  }

  console.log("");
  console.log(
    `🎯 Jobs passed KaziNest filter: ${filteredJobs.length}`
  );

  console.log(
    `🚫 Jobs rejected: ${rejectedCount}`
  );

  // ==========================================================
  // 5. FINAL DEDUPLICATION
  // ==========================================================

  const finalJobs =
    Array.from(
      new Map(
        filteredJobs.map(
          (job) => [
            job.external_id,
            job,
          ]
        )
      ).values()
    );

  console.log(
    `💎 Final unique jobs: ${finalJobs.length}`
  );

  // ==========================================================
  // 6. NOTHING TO SAVE
  // ==========================================================

  if (
    finalJobs.length === 0
  ) {
    console.log("");
    console.log(
      "⚠️ No ClimateChangeCareers jobs passed the filter."
    );

    console.log("");
    console.log(
      "Diagnostics:"
    );

    console.log(
      `Raw jobs: ${allJobs.length}`
    );

    console.log(
      `Unique jobs: ${uniqueJobs.length}`
    );

    console.log(
      `Rejected by filter: ${rejectedCount}`
    );

    return;
  }

  // ==========================================================
  // 7. SUPABASE UPSERT
  // ==========================================================

  const chunks =
    [];

  for (
    let i = 0;
    i < finalJobs.length;
    i += CHUNK_SIZE
  ) {
    chunks.push(
      finalJobs.slice(
        i,
        i + CHUNK_SIZE
      )
    );
  }

  console.log("");
  console.log(
    `💾 Saving ${finalJobs.length} jobs in ${chunks.length} chunks...`
  );

  let savedCount =
    0;

  let failedCount =
    0;

  for (
    let i = 0;
    i < chunks.length;
    i++
  ) {
    const chunk =
      chunks[i];

    const {
      error,
    } = await supabase
      .from(
        "external_jobs"
      )
      .upsert(
        chunk,
        {
          onConflict:
            "source,external_id",
        }
      );

    if (
      error
    ) {
      failedCount +=
        chunk.length;

      console.error("");
      console.error(
        `❌ Chunk ${i + 1}/${chunks.length} failed`
      );

      console.error(
        error
      );
    } else {
      savedCount +=
        chunk.length;

      console.log(
        `✅ Chunk ${i + 1}/${chunks.length} saved (${chunk.length} jobs)`
      );
    }
  }

  // ==========================================================
  // FINAL REPORT
  // ==========================================================

  console.log("");
  console.log(
    "=================================================="
  );
  console.log(
    "🏁 CLIMATECHANGCAREERS SCRAPER COMPLETE"
  );
  console.log(
    "=================================================="
  );

  console.log(
    `Raw jobs:           ${allJobs.length}`
  );

  console.log(
    `Unique jobs:        ${uniqueJobs.length}`
  );

  console.log(
    `Enriched jobs:      ${enrichedJobs.length}`
  );

  console.log(
    `Passed filter:      ${filteredJobs.length}`
  );

  console.log(
    `Final unique jobs:  ${finalJobs.length}`
  );

  console.log(
    `Saved successfully: ${savedCount}`
  );

  console.log(
    `Failed to save:     ${failedCount}`
  );

  console.log(
    "=================================================="
  );
  console.log("");
}

// ============================================================
// EXECUTION
// ============================================================

if (
  require.main === module
) {
  run()
    .then(() => {
      process.exit(0);
    })
    .catch((error) => {
      console.error(
        "❌ ClimateChangeCareers scraper crashed:",
        error?.stack ||
          error?.message ||
          error
      );

      process.exit(1);
    });
}

module.exports = run;