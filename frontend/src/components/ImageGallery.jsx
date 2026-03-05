import './ImageGallery.css';

export default function ImageGallery({ images, selectedIndex, onSelect }) {
    return (
        <div className="img-gallery">
            <h4 className="gallery-title">✦ 療癒圖像</h4>
            <div className="gallery-grid">
                {images.map((b64, i) => (
                    <div
                        key={i}
                        className={`gallery-item ${i === selectedIndex ? 'selected' : ''}`}
                        onClick={() => onSelect(i)}
                        role="button"
                        tabIndex={0}
                        aria-label={`圖像 ${i + 1}`}
                        onKeyDown={e => e.key === 'Enter' && onSelect(i)}
                    >
                        <img
                            src={`data:image/jpeg;base64,${b64}`}
                            alt={`生成圖像 ${i + 1}`}
                            loading="lazy"
                        />
                        {i === selectedIndex && (
                            <div className="gallery-check">✓</div>
                        )}
                        <div className="gallery-label">圖像 {i + 1}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
