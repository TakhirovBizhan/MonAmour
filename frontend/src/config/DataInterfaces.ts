export interface Artist {
  id: string;
  name: string;
  image: string;
  biography: string;
}

export interface Gallery {
  id: string;
  name: string;
  description: string;
  gallery_image: string;
}

export interface Category {
  id: string;
  name: string;
  description: string;
  created_at: string;
  updated_at: string;
}

interface Image {
  id: string;
  image_url: string;
}

export interface Painting {
  id: string;
  title: string;
  description: string;
  artist: Artist;
  gallery: Gallery;
  category: Category;
  technique: string;
  dimensions: string;
  price: string;           // Цена в виде строки (например, "30000.00")
  discounted_price: number; // Цена со скидкой в виде числа
  status: string;          // Например, "available"
  added_at: string;        // ISO дата в формате строки
  images: Image[];
}
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