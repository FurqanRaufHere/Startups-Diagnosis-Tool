type RedFlagListProps = {
  flags: string[];
};

export default function RedFlagList({ flags }: RedFlagListProps) {
  return (
    <article className="flags card">
      <h2>Red Flags</h2>
      {flags.length === 0 ? (
        <p>No critical flags found in this run.</p>
      ) : (
        <ul>
          {flags.map((flag) => (
            <li key={flag}>{flag}</li>
          ))}
        </ul>
      )}
    </article>
  );
}
