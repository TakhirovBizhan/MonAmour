// components/AddPaintingModal/AddPaintingModal.tsx
import React, { useState, useEffect } from 'react';
import styles from './AddPaintingModal.module.scss';
import { useAddPaintingMutation, useUploadImageBase64Mutation } from '../../../../../store/api/Products.api';
import Button from '../../../../../components/Button';
import Text from '../../../../../components/Text';
import { useGetCategoriesQuery } from '../../../../../store/api/Categories.api';
import { useGetArtistsQuery } from '../../../../../store/api/authors.api';
import { useGetGalleriesQuery } from '../../../../../store/api/Galleries.api';
import { PaintingPostType } from '../../../../../config/DataInterfaces';

export const AddPaintingModal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const [addPainting] = useAddPaintingMutation();
  const [uploadImageBase64] = useUploadImageBase64Mutation();

  const { data: categoriesData } = useGetCategoriesQuery();
  const { data: artistsData } = useGetArtistsQuery();
  const { data: galleryData } = useGetGalleriesQuery();

  const initialForm = {
    title: '',
    description: '',
    artist: '',
    gallery: '',
    category: '',
    technique: '',
    dimensions: '',
    price: '',
    status: 'available',
    images: [] as File[],
  };
  const [form, setForm] = useState(initialForm);
  const [previews, setPreviews] = useState<string[]>([]);

  useEffect(() => {
    setForm((prev) => ({
      ...prev,
      artist: prev.artist || (artistsData && artistsData.length > 0 ? artistsData[0].id : ''),
      gallery: prev.gallery || (galleryData && galleryData.length > 0 ? galleryData[0].id : ''),
      category: prev.category || (categoriesData && categoriesData.length > 0 ? categoriesData[0].id : ''),
    }));
  }, [artistsData, galleryData, categoriesData]);

  useEffect(() => {
    if (!form.images.length) {
      setPreviews([]);
      return;
    }
    const urls = form.images.map((f) => URL.createObjectURL(f));
    setPreviews(urls);
    return () => {
      urls.forEach((u) => URL.revokeObjectURL(u));
    };
  }, [form.images]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const target = e.target as HTMLInputElement;
    const { name, value, type, files } = target;
    if (type === 'file' && files) {
      setForm((prev) => ({ ...prev, images: [...prev.images, ...Array.from(files)] }));
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
    }
  };

  // Прочитать File как Data URL (включая префикс "data:image/...")
  const fileToDataURL = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        resolve(result);
      };
      reader.onerror = (error) => reject(error);
      reader.readAsDataURL(file);
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formEl = e.currentTarget;
    if (!formEl.checkValidity()) {
      formEl.reportValidity();
      return;
    }

    try {
      // 1) Загрузка изображений: получаем ids
      let imageIds: string[] = [];
      if (form.images.length > 0) {
        // Параллельно загружаем
        const uploadPromises = form.images.map(async (file) => {
          const dataUrl = await fileToDataURL(file);
          // Вызываем uploadImageBase64 с { image: dataUrl }
          const resp = await uploadImageBase64({ image: dataUrl }).unwrap();
          return resp.id;
        });
        imageIds = await Promise.all(uploadPromises);
      }

      // 2) Собираем payload
      const payload: PaintingPostType = {
        title: form.title,
        description: form.description,
        artist_id: form.artist, // в зависимости от того, как вы именуете поля в PaintingPostType
        gallery_id: form.gallery,
        category_id: form.category,
        technique: form.technique,
        dimensions: form.dimensions,
        price: form.price,
        status: 'available',
        image_ids: imageIds, // соответствует сериализатору: image_ids
      };

      // 3) Создаём запись картины
      await addPainting(payload).unwrap();
      // 4) Сброс
      setForm(initialForm);
      onClose();
    } catch (err) {
      console.error('Ошибка при загрузке или создании:', err);
      // Можно показывать уведомление
    }
  };

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <Button className={styles.closeBtn} onClick={onClose}>
          &times;
        </Button>
        <Text view="title">Добавить картину</Text>
        <form className={styles.form} onSubmit={handleSubmit} noValidate>
          <div className={styles.grid}>
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
                {artistsData?.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <Text view="p-18">Галерея</Text>
              <select name="gallery" value={form.gallery} onChange={handleChange} required>
                {galleryData?.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.name}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <Text view="p-18">Категория</Text>
              <select name="category" value={form.category} onChange={handleChange} required>
                {categoriesData?.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
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
              <input
                type="file"
                name="images"
                multiple
                accept="image/*"
                onChange={handleChange}
                required={form.images.length === 0}
              />
            </div>
          </div>

          {previews.length > 0 && (
            <div className={styles.previewGrid}>
              {previews.map((src, idx) => (
                <img key={idx} src={src} className={styles.previewImg} alt="preview" />
              ))}
            </div>
          )}

          <Button type="submit" className={styles.submitBtn}>
            Добавить
          </Button>
        </form>
      </div>
    </div>
  );
};

export default AddPaintingModal;
