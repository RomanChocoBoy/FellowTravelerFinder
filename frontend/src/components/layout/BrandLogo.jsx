import logoUrl from '@logo'

const SIZES = {
  sm: { img: 32, title: '0.95rem' },
  md: { img: 40, title: '1.1rem' },
  lg: { img: 56, title: '1.35rem' },
}

export default function BrandLogo({ size = 'md', centered = false, showTagline = false }) {
  const s = SIZES[size] || SIZES.md

  return (
    <div className={`brand-logo ${centered ? 'brand-logo--center' : ''}`}>
      <img src={logoUrl} alt="" width={s.img} height={s.img} className="brand-logo__img" />
      <div className="brand-logo__text">
        <span className="brand-logo__title" style={{ fontSize: s.title }}>
          Поиск Попутчиков
        </span>
        {showTagline && <span className="brand-logo__tagline">Поездки и встречи на дороге</span>}
      </div>
    </div>
  )
}
