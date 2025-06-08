// components/AddPaintingModal/AddPaintingModal.tsx
import React, { useState, useEffect } from 'react';

import styles from './AddPaintingModal.module.scss';
import { useAddPaintingMutation } from '../../../../../store/api/Products.api';
import Button from '../../../../../components/Button';
import Text from '../../../../../components/Text';

const ARTISTS = [
  { id: '1', name: 'Катя Иванова' },
  { id: '2', name: 'Иван Петров' },
];
const GALLERIES = [
  { id: '1', name: 'Галерея №1' },
  { id: '2', name: 'Галерея №2' },
];
const CATEGORIES = [
  { id: '1', name: 'Пейзаж' },
  { id: '2', name: 'Портрет' },
];
const STATUSES = [
  { value: 'available', label: 'Available' },
  { value: 'sold', label: 'Sold' },
];

const initialForm = {
  title: '',
  description: '',
  artist: ARTISTS[0].id,
  gallery: GALLERIES[0].id,
  category: CATEGORIES[0].id,
  technique: '',
  dimensions: '',
  price: '',
  status: STATUSES[0].value,
  images: [] as File[],
};

export const AddPaintingModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const [addPainting, { isLoading }] = useAddPaintingMutation();
  const [form, setForm] = useState(initialForm);
  const [previews, setPreviews] = useState<string[]>([]);

  useEffect(() => {
    if (!form.images.length) {
      setPreviews([]);
      return;
    }
    const urls = form.images.map((f) => URL.createObjectURL(f));
    setPreviews(urls);
    return () => urls.forEach((u) => URL.revokeObjectURL(u));
  }, [form.images]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value, type, files } = e.target as HTMLInputElement;
    if (type === 'file' && files) {
      setForm((prev) => ({ ...prev, images: [...prev.images, ...Array.from(files)] }));
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // simple HTML5 validation
    const formEl = e.currentTarget;
    if (!formEl.checkValidity()) {
      formEl.reportValidity();
      return;
    }
    const data = new FormData();
    Object.entries(form).forEach(([key, val]) => {
      if (key === 'images') {
        (val as File[]).forEach((f) => data.append('images', f));
      } else {
        data.append(key, val as string);
      }
    });
    await addPainting(data as any);
    setForm(initialForm);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <Button className={styles.closeBtn} onClick={onClose}>
          &times;
        </Button>
        <Text view="title">Добавить картину</Text>
        <form className={styles.form} onSubmit={handleSubmit} encType="multipart/form-data" noValidate>
          <div className={styles.grid}>
            {/** Required fields */}
            {[
              { label: 'Заголовок', name: 'title', type: 'text' },
              { label: 'Техника', name: 'technique', type: 'text' },
              { label: 'Размеры', name: 'dimensions', type: 'text' },
              { label: 'Цена', name: 'price', type: 'text' },
            ].map((field) => (
              <div className={styles.field} key={field.name}>
                <Text view="p-18">{field.label}</Text>
                <input
                  name={field.name}
                  type={field.type}
                  value={(form as any)[field.name]}
                  onChange={handleChange}
                  required
                />
              </div>
            ))}
            <div className={styles.field}>
              <Text view="p-18">Артист</Text>
              <select name="artist" value={form.artist} onChange={handleChange} required>
                {ARTISTS.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <Text view="p-18">Галерея</Text>
              <select name="gallery" value={form.gallery} onChange={handleChange} required>
                {GALLERIES.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.name}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <Text view="p-18">Категория</Text>
              <select name="category" value={form.category} onChange={handleChange} required>
                {CATEGORIES.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <Text view="p-18">Статус</Text>
              <select name="status" value={form.status} onChange={handleChange} required>
                {STATUSES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <Text view="p-18">Описание</Text>
              <textarea name="description" value={form.description} onChange={handleChange} required />
            </div>
            <div className={styles.field}>
              <Text view="p-18">Изображения</Text>
              <input type="file" name="images" multiple accept="image/*" onChange={handleChange} required />
            </div>
          </div>
          {previews.length > 0 && (
            <div className={styles.previewGrid}>
              {previews.map((src, idx) => (
                <img key={idx} src={src} className={styles.previewImg} alt="preview" />
              ))}
            </div>
          )}
          <Button type="submit" disabled={isLoading} className={styles.submitBtn}>
            {isLoading ? 'Сохранение...' : 'Добавить'}
          </Button>
        </form>
      </div>
    </div>
  );
};

export default AddPaintingModal;
