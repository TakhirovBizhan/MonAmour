import Button from '../../../components/Button';
import Loader from '../../../components/Loader';
import Text from '../../../components/Text';
import { useAuth } from '../../../hooks/useAuth/AuthContext';
import { useGetProfileQuery } from '../../../store/api/Auth.api';
import s from './Profile.module.scss';

const Profile = () => {
  const { data: profileData, isLoading: loading } = useGetProfileQuery();
  const { logout } = useAuth();

  return (
    <div className={s.wrapper}>
      {loading ? (
        <Loader size="l" />
      ) : (
        <>
          <div className={s.root}>
            <img className={s.img} src={profileData?.avatar} alt={'avatar'} />
            <div>
              <Text view="min-title">Username: {profileData?.name}</Text>
              <Text view="p-18">Email: {profileData?.email}</Text>
            </div>
          </div>
          <Button className={s.button} onClick={logout}>
            Exit
          </Button>
        </>
      )}
    </div>
  );
};

export default Profile;
