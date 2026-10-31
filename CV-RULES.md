# CV rules for AI agents

Read this whole file before you create or edit any CV in this repo. These are David
Adegbola's standing rules. The repo is `david-adegbola/cv`. Each CV is tailored to one job,
written in LaTeX and published by GitHub Actions to https://david-adegbola.github.io/cv/.

## 0. How strictly to follow these rules

- These rules are requirements, not suggestions. Do not leave anything out, add anything or
  change anything because you think it would be better (e.g. "to avoid a stale detail").
  If you believe a rule is wrong, follow it anyway and raise the concern in your report.
- If a request conflicts with a rule, follow the rule and tell David which rule you followed.
- The facts in section 7 are the single source of truth. Every CV must agree with them.
  If a request gives a fact that differs from section 7 (an employer name, dates, a title,
  a card, a licence), STOP before writing any files and ask David:
  "Is this a correction for all CVs, or only for this one?"
  - Correction for all: update every CV in `roles/*/` and section 7 of this file in the same commit.
  - Only for this CV: do it, and list it under "Differences" in your report.
- If a fact you need is missing, ask. Never guess and never invent.
- Mandatory in every CV: the age in the summary opener, the References section, the honest
  Finnish line, and the certificate wording.
- In your report, separate:
  (a) what the request asked for, and
  (b) what you decided yourself.
  (b) should normally be empty.

## 1. Repo layout and workflow for a new CV

- One folder per job: `roles/<role-slug>/` containing
  - `cv-fi.tex` (Finnish; not needed for en-only roles),
  - `cv-en.tex` (English), and
  - `job.md`.
- Each role sets its language in job.md: fi-first (default), en-first or en-only.
  Use en-first or en-only for employers that work in English.
  - Write it as the line `- **Language:** fi-first` (or `en-first` / `en-only`) under the
    `Languages` line. No line means fi-first.
  - fi-first: `cv-fi.tex` is the main version. en-first: `cv-en.tex` is the main version.
    en-only: only `cv-en.tex` is built.
- Start by copying the closest existing role folder, then tailor the copy.
- Preamble:
  - `\cvrole{...}` sets the footer role text.
  - Finnish files also need `\cvlang{fi}`, and use `\cvt{key}` for the fixed labels
    (e.g. `\section{\cvt{experience}}`).
- `job.md` is PUBLIC. It starts with a `# ` heading (it becomes the title on the role's public
  employer page; never put a company name in it), then lists: role, job type, languages (mark the main
  one), PDF names (including the combined one), created date (today), `Photo: no`, and notes
  about the CV's content (what was left out and why).
- Everything about the application itself is PRIVATE and goes in the git-ignored
  `applications/job-details/<role-slug>.md`: company / agency, location, job-ad link, contact
  person and phone, deadline, status, and a summary of the ad. Never put these in `job.md`,
  the README, commit messages, `.tex` comments or the role folder name.
- Name role folders after the job type, not the employer (e.g. `roles/steel-installer/`,
  not `roles/installer-<company>/`); the folder name is part of the public PDF URL.
- Compile each file twice with pdflatex from inside its role folder:
  `cd roles/<role> && pdflatex cv-fi.tex && pdflatex cv-fi.tex`
  - Target ONE page.
  - The log must have no "Overfull" warnings.
  - Render the PDF to an image and look at it.
- Make the single combined PDF, the file David actually submits:
  `shared/combine.sh roles/<role>` writes `roles/<role>/cv-combined.pdf`, with the main
  version first: Finnish then English for fi-first, English then Finnish for en-first. For
  en-only it is the English CV on its own, so the file to submit always has the same name.
  - Every fi-first and en-first role has both `cv-fi.tex` and `cv-en.tex`; an en-only role has
    only `cv-en.tex`. Every role gets a combined PDF.
  - Check it: both versions are there in that order, and the page count is the two added
    together (normally 1 + 1 = 2 pages; 1 page for en-only).
  - The GitHub Action builds and publishes it automatically as
    `david-adegbola-<role-slug>.pdf`. Never commit it (PDFs are git-ignored).
- Do NOT list the role or its links in README.md or on the public root page (David's decision,
  2026-10-30: links are shared one at a time). The GitHub Action builds the role's employer page
  `/r/<role-slug>/` automatically (`site/build.py`).
- Commit only the .tex and .md files, e.g. "Add CV: <Role> (FI + EN)" ("(EN)" for en-only), and
  push to main.
- Wait for the GitHub Action "Build CVs and deploy to Pages" to finish with build and deploy
  both successful. Then check that each link returns HTTP 200:
  - employer page: `https://david-adegbola.github.io/cv/r/<role-slug>/`
  - combined: `https://david-adegbola.github.io/cv/david-adegbola-<role-slug>.pdf`
  - one language: `https://david-adegbola.github.io/cv/david-adegbola-<role-slug>-<lang>.pdf`
- Report to David:
  - the employer link `https://david-adegbola.github.io/cv/r/<role-slug>/` first (the link he
    sends), then the combined PDF and both language links;
  - every fact that now differs from his other CVs;
  - anything you left out and why;
  - what you decided yourself (see section 0).
- If a fact changes, update ALL CVs so they agree.

## 2. Fitting on one page

Try these first, in this order:
1. Compact minor jobs to one-line entries: courier, AV volunteer, Founder in Residence,
   Nigerian jobs.
2. Merge Cards and Languages into the Skills section as rows.
3. Remove duplicates between the header, summary and skills.
4. Shorten the summary.

Never drop:
- the age;
- the References section;
- facts from the work certificate.

## 3. Layout rules (ATS = applicant tracking systems that scan CVs)

- Use the helpers in `shared/cv-style.sty`. Never use `tabular`/`longtable` for
  label/value or date/job rows: they extract column by column, which separates dates and
  labels from their content.
  - `\cvline[label width]{Label:}{value}` for contact details, skills, education and languages.
  - `\begin{cventry}{dates}{title line} ... \end{cventry}` for jobs. Put detail lines inside,
    separated by `\par`, and tags last with `\sotagrow{tag-one,tag-two}`.
  - A one-line minor job: `\begin{cventry}{Apr 2025--Aug 2025}{\textbf{Title}, Employer, Place: what you did.}\end{cventry}`
  - The default label width is `\cvlabelw` (3.3cm). Widen it with
    `\setlength{\cvlabelw}{3.9cm}` after `\begin{document}` if the dates are long.
  - Keep the gap between label and value small (`\cvlabelsep`, 5pt). With a wider gap, PDF
    text extraction splits short rows again.
- The summary stays in `\begin{tabular}{p{0.9\textwidth}} ... \end{tabular}`, with two
  paragraphs separated by `\\\\` and a blank line.
- Use the standard headings: Summary / Yhteenveto, Skills / Taidot,
  Work Experience / Työkokemus, Education / Koulutus, Languages / Kielet, Cards / Kortit,
  References / Suosittelijat, and the optional Hobbies / Harrastukset (`\section{\cvt{hobbies}}`,
  added 2026-10-31).
- Contact details go in the body (inside `\begin{cvheader}...\end{cvheader}`), never only in
  a footer.
- Use one date format per CV, with each date on the same line as its job:
  - English: "Apr 2025--Aug 2025".
  - Finnish: "4/2025--8/2025".
  - The certificate job may use exact dates: "18.8.2025--7.10.2025" / "18 Aug 2025--7 Oct 2025".
- Use the job ad's own keywords, but only for things David has done or says he wants to learn.
- Spell out acronyms and cards once, e.g. "Occupational safety card (työturvallisuuskortti)".
- Before committing, run `pdftotext cv-xx.pdf -` and check that:
  - all text is present, with no broken characters;
  - every job's dates, title and employer come out on one line;
  - every label comes out on the same line as its value.
- Footer:
  - It is automatic: it appears only when a CV has more than one page; one-page CVs have none.
  - Never add a footer by hand.
  - The page count comes from the previous pdflatex run, so always compile twice.
- Photo: ALWAYS off in committed CVs. Never add `\cvphoto{...}`, even if a request asks for it.
  Write `Photo: no` in job.md. David adds the photo locally when he needs it.
- Every CV ends with a References section:
  - Finnish: `\section{\cvt{references}}` then `\cvt{refsavailable}`.
  - English: `\section{References}` then `Available on request.`

## 4. Summary style

- Write it in the first person. Always start with the age; it is required:
  - English: "Hi! I'm David, 24, ..."
  - Finnish: "Hei! Olen David, 24-vuotias ..."
  - The age is 24 as of October 2026. If you believe it may be out of date, ask David for
    his current age; never leave it out.
  - Add "a Sustainable Forest Bioeconomy student at the University of Eastern Finland" only
    when it helps the application, e.g. for part-time jobs. Leave it out for other full-time jobs.
  - Exception (David, 2026-10-31): forestry, forest bioeconomy, trainee and research roles keep the
    student line even when the work is full-time, because the degree is the main fit.
- Paragraph 1: the relevant work story in plain words, using specific facts. The employer's
  own words from the certificate are best.
- Paragraph 2: how he works, then why he fits this job. It always ends with an honest line on
  Finnish:
  - English: "My Finnish is still basic, and I'm actively studying it."
  - Finnish: "Suomen kielen taitoni on vielä perustasolla, ja opiskelen sitä aktiivisesti."
- Include only what the employer needs. Leave out:
  - his move from Vaasa to Joensuu;
  - what the job would give him (practising Finnish, getting to know people);
  - details that only repeat the Work Experience section.

## 5. Making the writing sound human (no AI tells)

Check the summary and every experience line in both languages:
- No buzzwords. Avoid words like crucial, key, enhance, showcase, foster, leverage,
  passionate, dynamic, results-driven, "proven track record", "growing sector",
  "team collaboration".
- No padding with "-ing" phrases ("…, ensuring safety").
- No "not only… but also".
- No forced lists of three adjectives.
- No em dashes.
- No sales tone.
- No clichés such as "this taught me the importance of…", "I learned a lot", or
  "I'm passionate about".
  Replace them with a concrete fact, e.g. "My employer rated my work excellent".
- Use active voice and plain verbs (is, has, did). Vary sentence length. Cut filler.
- Finnish must read as natural, plain Finnish, not a stiff translation.
- Last pass: ask yourself "what still makes this look AI-written?", then fix it.
- If Claude Code skills named `humanizer` and `developing-essays` are available, run both on
  the text.

## 6. Honesty and privacy (this repo is PUBLIC)

- Never claim experience, skills, cards or licences David doesn't have. Things he lacks may
  only appear as things he wants to learn.
  - Not held: welding, welding certificates, hot-work card (tulityökortti),
    forklift card (trukkikortti), reading drawings.
  - Drawings may only appear as "learning to read assembly drawings" /
    "opettelen lukemaan asennuspiirustuksia".
  - B driving licence: NOT confirmed. Leave it out unless David confirms it.
- Never commit:
  - his work certificate (työtodistus);
  - any personal ID number (henkilötunnus);
  - his street address;
  - named personal references.
- `.gitignore` blocks PDFs, `applications/`, work certificates, ID scans, office documents and
  every image except `shared/photos/david.jpg`. Never use `git add -f` to get round it; if a file
  is ignored, it must stay local.
- PDFs are git-ignored; keep it that way. The certificate PDF may sit in the repo root,
  ignored. You may read it locally, but never copy text from it into the repo except the
  wordings in section 7.
- Before every commit, search the staged files for ID-number patterns like `DDMMYY-XXXX`.

## 7. Canonical facts (use exactly these; never invent others)

- Name: David Adegbola, age 24 (as of October 2026), lives in Joensuu, Finland.
  Phone +358 46 800 7210, email adavidadegbola@gmail.com.
- Languages: Finnish basic (actively studying), English fluent, Yoruba native.
- Computer skills: Microsoft Office (David, 2026-10-31); Microsoft Active Directory from the VAMK
  IT studies.
- Cards: occupational safety card (työturvallisuuskortti). The hygiene passport (hygieniapassi)
  is only listed for food or retail jobs.
- Main job, following his work certificate wording exactly:
  - Title: Asentaja (English: Fitter), Axioma Servisas UAB, 18.8.2025–7.10.2025.
  - Project:
    - Finnish: "sähkösuodattimen uudelleenrakennushanke".
    - English: "electrostatic precipitator rebuild project".
    - Do NOT write "recovery boiler" / "soodakattila", "boiler renovation" or "Alvasaar OÜ".
  - Skills:
    - Finnish: "Kulmahiomakoneen käyttö ja nostolaitteiden käyttö."
    - English: "Used angle grinders and lifting equipment."
  - Rating: kiitettävä (English: excellent).
  - Conduct:
    - Finnish: "Vastuuntuntoinen ja tunnollinen työntekijä, halukas oppimaan ja ottamaan vastuuta."
    - English: "A responsible and conscientious employee, eager to learn and to take responsibility."
  - From David, not on the certificate (keep): the work was at the UPM Kaukas pulp mill,
    Lappeenranta; he kept the work site clean, tracked tools and materials, and worked to
    the mill's strict safety rules.
  - Unconfirmed: "supervised by a foreman". Don't add it to new CVs.
- Independent Courier (Finnish: Lehdenjakaja): Finnbox and SSM, Vaasa, Apr 2025–Aug 2025.
  Early-morning delivery routes alone.
- Audio-Visual Volunteer (Finnish: AV-vapaaehtoinen): Vaasa City Church, Vaasa,
  Nov 2024–Aug 2026. Sound and video every weekend.
- Founder in Residence: Vaasa Startup Factory, Jun 2026–Aug 2026. Researched user needs with
  interviews and calls, then built and pitched hetkin.app with a team.
- Nigeria:
  - Salesperson, Desire Feeds, Lagos, Mar 2019–Sep 2020. Feed sales, advice, cash balancing.
  - Sales Assistant and Kitchen Helper, Bunmi Pastries, Ibadan, Sep 2016–Jun 2018.
  - For non-sales jobs, use one line: "Sales and customer service jobs in Nigeria
    (Desire Feeds, Bunmi Pastries)", Sep 2016–Sep 2020.
- Education:
  - B.Sc Sustainable Forest Bioeconomy, University of Eastern Finland, 2026–present.
  - B.Eng studies, Information Technology, VAMK (Vaasa University of Applied Sciences),
    2024–2026. Not completed; included Microsoft Active Directory.
  - OND in Computer Science, The Polytechnic, Ibadan, Nigeria, 2019–2022.
- Tailoring by job type:
  - Technical / industrial jobs: drop video/graphics work, Microsoft Office and sales lines.
    Keep IT to one line ("Basic computer skills").
  - Exception (David, 2026-10-31): trainee, office and student roles at industrial companies may
    list Microsoft Office and Microsoft Active Directory.
  - Sales jobs: keep the sales detail and the volunteering / video work.

## 8. Changing these rules

Only David changes these rules. When he gives a new standing rule ("always", "from now on",
"every CV"), add it to the right section of this file in the same commit as the CV change.
`facts.json` is generated from sections 6 and 7 for the employer pages and the JobDesk app (a
private repo that reads this one): after changing either section, run `python3 site/facts.py`
and commit `facts.json` in the same commit. This file stays the authority; the GitHub Action
fails if the two differ.
Before starting any CV task, read this file in full. If a request differs from a fact in
section 7, stop before editing and ask David: "Is this a correction for all CVs, or only for
this one?"
