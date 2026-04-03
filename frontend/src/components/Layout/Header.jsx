export default function Header({ title, subtitle }) {
  return (
    <header className="header">
      <div>
        <div className="header-title">{title}</div>
        {subtitle && <div className="header-subtitle">{subtitle}</div>}
      </div>
    </header>
  );
}
