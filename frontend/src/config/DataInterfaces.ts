export type ICategory = {
  id: number;
  name: string;
  image: string;
  creationAt: Date;
  updatedAt: Date;
};

export type IData = {
  id: number;
  title: string;
  price: number;
  description: string;
  images: string[];
  category: ICategory;
  creationAt: string;
  updatedAt: string;
};

export type TFilters = {
  price_min: number | null,
  price_max: number | null
}

export type registerForm = {
  name: string,
  email: string,
  password: string
}

export type userRegType = {
  name: string,
  email: string,
  password: string
  avatar: string
}

export type userRegResponce = {
  email: string,
  password: string,
  name: string,
  avatar: string,
  role: string,
  id: number
}

export type userLogType = {
  email: string,
  password: string
}

export type userLogResponce = {
  access_token: string,
  refresh_token: string
}