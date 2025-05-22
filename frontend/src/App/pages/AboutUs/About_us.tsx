import Text from '../../../components/Text';
import s from './About_us.module.scss';
const About_us = () => {
  return (
    <div className={s.wrapper}>
      <Text view="title">E-commerse mock service</Text>
      <Text view="p-20"> What do you call a cow in an earthquake? A milkshake.</Text>
    </div>
  );
};

export default About_us;
