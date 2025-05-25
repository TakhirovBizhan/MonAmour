// components/RedactModal/RedactModal.tsx
import React, { useState } from 'react';
import Text from '../../../../components/Text';
import styles from './Redact.module.scss';
import { useUpdateMutation } from '../../../../store/api/Auth.api';
import { userRegResponce } from '../../../../config/DataInterfaces';

interface RedactModalProps {
  data: userRegResponce;
  isOpen: boolean;
  onClose: () => void;
}

const RedactModal: React.FC<RedactModalProps> = ({ data, isOpen, onClose }) => {
  // Хуки всегда на самом верху
  const [username, setUsername] = useState(data.username);
  const [email, setEmail] = useState(data.email);
  const [firstName, setFirstName] = useState(data.first_name);
  const [lastName, setLastName] = useState(data.last_name);

  const [updateUser, { error: addError }] = useUpdateMutation();

  async function handleRedactBtn() {
    const id = localStorage.getItem('currentUser');
    if (id) {
      const resp = await updateUser({ id, username, email, first_name: firstName, last_name: lastName });
      console.log(resp);
      console.log(addError);
      onClose();
    }
  }

  // После инициализации хуков — ранний выход, если не открыт
  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log({ username, email, firstName, lastName });
    // здесь ваш код отправки
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeBtn} onClick={onClose}>
          &times;
        </button>
        <fieldset className={styles.fieldset}>
          <legend className={styles.legend}>
            <Text view="p-20">Форма редактирования</Text>
          </legend>
          <form className={styles.form} onSubmit={handleSubmit}>
            <label className={styles.label}>
              <Text view="p-18">Имя пользователя</Text>
              <input
                required
                type="text"
                className={styles.input}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </label>

            <label className={styles.label}>
              <Text view="p-18">Почта</Text>
              <input
                type="email"
                required
                className={styles.input}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </label>

            <label className={styles.label}>
              <Text view="p-18">Имя</Text>
              <input
                required
                type="text"
                className={styles.input}
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </label>

            <label className={styles.label}>
              <Text view="p-18">Фамилия</Text>
              <input
                required
                type="text"
                className={styles.input}
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </label>

            <button onClick={handleRedactBtn} className={styles.submitBtn}>
              Сохранить
            </button>
          </form>
        </fieldset>
      </div>
    </div>
  );
};

export default RedactModal;
