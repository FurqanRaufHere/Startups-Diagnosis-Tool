import UploadForm from "./components/UploadForm";

export default function HomePage() {
  return (
    <main>
      <section className="hero card">
        <p className="eyebrow">AI DUE DILIGENCE STUDIO</p>
        <h1>Venture Lens</h1>
        <p>
          Turn raw pitch decks into an investment-grade risk narrative with red flags,
          weighted scoring, and auto-generated memo drafts.
        </p>
      </section>

      <section className="stagger">
        <UploadForm />
      </section>
    </main>
  );
}
