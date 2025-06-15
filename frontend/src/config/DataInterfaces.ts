export interface Artist {
  id: string;
  name: string;
  image: string;
  biography: string;
}

export type PostOrder = {
  "user_id": string,
  "status": string,
  "street": string,
  "house_number": string,
  "city": string,
  "postal_code": string,
  "address_comment"?: string,
  "painting_ids": string[]
}

export type OrderResponse = {
  id: string
  "user": string,
  "status": string,
  "street": string,
  "house_number": number,
  "city": string,
  "postal_code": number,
  "address_comment"?: string,
  "payment_method": "card" | 'cash',
  "phone_number": string,
  "items": orderItem[],
  order_date: string
}

export type orderItem = {
  "id": string,
  "order": string,
  "painting": Painting,
  "price_at_purchase": number,
  "purchased_at": string
}

export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;       // может быть пусто
  role?: string;        // может быть пусто или 'buyer'/'admin'
  date_joined: string;  // ISO-строка
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

export interface Image {
  id: string;
  image_url: string;
}

export interface IPaintingData {
  count: number;
  next: unknown;
  previous: unknown;
  results: Painting[]
}

export interface PaintingPostType {
  id?: string;
  title: string;
  description: string;
  artist_id: string;
  gallery_id: string;
  category_id: string;
  technique: string;
  dimensions: string;
  price: string;
  status: 'available' | 'sold';
  image_ids: string[];
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
  id: string,
  username: string,
  email: string,
  first_name: string,
  last_name: string
}

export type userLogType = {
  email: string,
  password: string
}

export type userLogResponce = {
  access_token: string,
  refresh_token: string
}