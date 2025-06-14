// components/EditPaintingModal/EditPaintingModal.tsx
import React, { useState, useEffect } from 'react';
import styles from './AddPaintingModal.module.scss';
import { useUploadImageBase64Mutation, useRedactPaintingMutation } from '../../../../../store/api/Products.api';
import Button from '../../../../../components/Button';
import Text from '../../../../../components/Text';
import { useGetCategoriesQuery } from '../../../../../store/api/Categories.api';
import { useGetArtistsQuery } from '../../../../../store/api/authors.api';
import { useGetGalleriesQuery } from '../../../../../store/api/Galleries.api';
import { Painting, Image } from '../../../../../config/DataInterfaces'; // ваш интерфейс Painting
import { PaintingPostType } from '../../../../../config/DataInterfaces';

interface EditPaintingModalProps {
  isOpen: boolean;
  onClose: () => void;
  paintingToEdit: Painting;
}

const EditPaintingModal: React.FC<EditPaintingModalProps> = ({ isOpen, onClose, paintingToEdit }) => {
  const [uploadImageBase64, { isLoading: isUploading }] = useUploadImageBase64Mutation();
  const [redactPainting, { isLoading: isSaving }] = useRedactPaintingMutation();

  // Справочники
  const { data: categoriesData } = useGetCategoriesQuery();
  const { data: artistsData } = useGetArtistsQuery();
  const { data: galleryData } = useGetGalleriesQuery();

  // Начальное состояние текстовых полей
  const emptyFormValues = {
    title: '',
    description: '',
    technique: '',
    dimensions: '',
    price: '',
    status: 'available',
    artist: '',
    gallery: '',
    category: '',
  };
  const [form, setForm] = useState(() => ({ ...emptyFormValues }));

  // Существующие изображения (id и image_url)
  const [existingImages, setExistingImages] = useState<Array<Image>>([]);
  // Новые выбранные файлы
  const [newImages, setNewImages] = useState<File[]>([]);
  // Превью для новых файлов (object URLs)
  const [newImagePreviews, setNewImagePreviews] = useState<string[]>([]);

  // При открытии или изменении paintingToEdit: заполняем поля и existingImages
  useEffect(() => {
    if (isOpen) {
      // Заполняем form из paintingToEdit
      setForm({
        title: paintingToEdit.title || '',
        description: paintingToEdit.description || '',
        technique: paintingToEdit.technique || '',
        dimensions: paintingToEdit.dimensions || '',
        price: paintingToEdit.price || '',
        status: paintingToEdit.status || 'available',
        artist: paintingToEdit.artist?.id || '',
        gallery: paintingToEdit.gallery?.id || '',
        category: paintingToEdit.category?.id || '',
      });
      // Заполняем существующие изображения
      setExistingImages(paintingToEdit.images.map((img) => ({ id: img.id, image_url: img.image_url })));
      // Сбрасываем новые
      setNewImages([]);
    } else {
      // При закрытии: очистка
      setForm({ ...emptyFormValues });
      setExistingImages([]);
      setNewImages([]);
      setNewImagePreviews([]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen, paintingToEdit]);

  // При изменении newImages создаём objectURLs и очищаем старые
  useEffect(() => {
    // Очистка предыдущих object URLs
    newImagePreviews.forEach((u) => URL.revokeObjectURL(u));
    // Создаём новые превью
    const urls = newImages.map((file) => URL.createObjectURL(file));
    setNewImagePreviews(urls);
    // Очистить при unmount
    return () => {
      urls.forEach((u) => URL.revokeObjectURL(u));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [newImages]);

  // При изменении справочников, если поле ещё пустое, заполняем дефолтным
  useEffect(() => {
    setForm((prev) => ({
      ...prev,
      artist: prev.artist || (artistsData && artistsData.length > 0 ? artistsData[0].id : ''),
      gallery: prev.gallery || (galleryData && galleryData.length > 0 ? galleryData[0].id : ''),
      category: prev.category || (categoriesData && categoriesData.length > 0 ? categoriesData[0].id : ''),
    }));
  }, [artistsData, galleryData, categoriesData]);

  // Обработчик изменения полей
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const target = e.target as HTMLInputElement;
    const { name, value, type, files } = target;
    if (type === 'file' && files) {
      // Добавляем новые файлы в newImages
      setNewImages((prev) => [...prev, ...Array.from(files)]);
    } else {
      setForm((prev) => ({ ...prev, [name]: value }));
    }
  };

  // Удаление существующего изображения по id
  const handleRemoveExistingImage = (id: string) => {
    setExistingImages((prev) => prev.filter((img) => img.id !== id));
  };
  // Удаление нового файла по индексу
  const handleRemoveNewImage = (index: number) => {
    setNewImages((prev) => prev.filter((_, idx) => idx !== index));
  };

  // Конвертация File -> Data URL
  const fileToDataURL = (file: File): Promise<string> =>
    new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        resolve(result);
      };
      reader.onerror = (error) => reject(error);
      reader.readAsDataURL(file);
    });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formEl = e.currentTarget;
    if (!formEl.checkValidity()) {
      formEl.reportValidity();
      return;
    }
    try {
      // 1. Загружаем новые файлы, если есть
      let newImageIds: string[] = [];
      if (newImages.length > 0) {
        const uploadPromises = newImages.map(async (file) => {
          const dataUrl = await fileToDataURL(file);
          const resp = await uploadImageBase64({ image: dataUrl }).unwrap();
          return resp.id;
        });
        newImageIds = await Promise.all(uploadPromises);
      }
      // 2. Итоговые image_ids: существующие после удаления + новые
      const keptExistingIds = existingImages.map((img) => img.id);
      const imageIds = [...keptExistingIds, ...newImageIds];

      // 3. Payload для редактирования
      const payload: PaintingPostType & { id: string } = {
        id: paintingToEdit.id,
        title: form.title,
        description: form.description,
        technique: form.technique,
        dimensions: form.dimensions,
        price: form.price,
        status: 'available',
        artist_id: form.artist,
        gallery_id: form.gallery,
        category_id: form.category,
        image_ids: imageIds,
      };

      console.log(payload);
      // 4. Вызываем редактирование
      await redactPainting(payload).unwrap();
      // 5. Закрываем — сброс состояния произойдет в useEffect
      onClose();
    } catch (err) {
      console.error('Ошибка при сохранении картины:', err);
      // Можно показать уведомление пользователю
    }
  };

  if (!isOpen) return null;

  const isSubmitting = isUploading || isSaving;

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <Button className={styles.closeBtn} onClick={onClose} disabled={isSubmitting}>
          &times;
        </Button>
        <Text view="title">Редактировать картину</Text>
        <form className={styles.form} onSubmit={handleSubmit} noValidate>
          <div className={styles.grid}>
            {/* Текстовые поля */}
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
                  disabled={isSubmitting}
                />
              </div>
            ))}

            {/* Селекты artist, gallery, category */}
            <div className={styles.field}>
              <Text view="p-18">Артист</Text>
              <select name="artist" value={form.artist} onChange={handleChange} required disabled={isSubmitting}>
                {artistsData?.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <Text view="p-18">Галерея</Text>
              <select name="gallery" value={form.gallery} onChange={handleChange} required disabled={isSubmitting}>
                {galleryData?.map((g) => (
                  <option key={g.id} value={g.id}>
                    {g.name}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <Text view="p-18">Категория</Text>
              <select name="category" value={form.category} onChange={handleChange} disabled={isSubmitting}>
                <option value="">Без категории</option>
                {categoriesData?.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Статус */}
            <div className={styles.field}>
              <Text view="p-18">Статус</Text>
              <select name="status" value={form.status} onChange={handleChange} required disabled={isSubmitting}>
                <option value="available">В наличии</option>
                <option value="sold">Продано</option>
              </select>
            </div>

            {/* Описание */}
            <div className={styles.field}>
              <Text view="p-18">Описание</Text>
              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                required
                disabled={isSubmitting}
              />
            </div>

            {/* Загрузка новых изображений */}
            <div className={styles.field}>
              <Text view="p-18">Новые изображения</Text>
              <input
                type="file"
                name="images"
                multiple
                accept="image/*"
                onChange={handleChange}
                disabled={isSubmitting}
                // Требуем только если после удаления существующих нет ни одного, и не выбрано новых
                required={existingImages.length === 0 && newImages.length === 0}
              />
            </div>
          </div>

          {/* Превью существующих изображений */}
          {existingImages.length > 0 && (
            <div className={styles.previewGrid}>
              {existingImages.map((img, idx) => (
                <div key={img.id} className={styles.previewWrapper}>
                  <img src={img.image_url} className={styles.previewImg} alt={`existing-${idx}`} />
                  <button
                    type="button"
                    className={styles.removeBtn}
                    onClick={() => handleRemoveExistingImage(img.id)}
                    disabled={isSubmitting}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
          {/* Превью новых файлов */}
          {newImages.length > 0 && (
            <div className={styles.previewGrid}>
              {newImages.map((file, idx) => (
                <div key={idx} className={styles.previewWrapper}>
                  <img src={newImagePreviews[idx]} className={styles.previewImg} alt={`new-${idx}`} />
                  <button
                    type="button"
                    className={styles.removeBtn}
                    onClick={() => handleRemoveNewImage(idx)}
                    disabled={isSubmitting}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          <Button type="submit" className={styles.submitBtn} disabled={isSubmitting}>
            {isSubmitting ? 'Сохраняем...' : 'Сохранить'}
          </Button>
        </form>
      </div>
    </div>
  );
};

export default EditPaintingModal;
