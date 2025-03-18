<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('paintings', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->text('description')->nullable();

            // Внешние ключи
            $table->unsignedBigInteger('artist_id');
            $table->unsignedBigInteger('gallery_id')->nullable();

            $table->string('technique')->nullable();
            $table->string('dimensions')->nullable();
            $table->decimal('price', 12, 2)->nullable();
            $table->string('image_url')->nullable();
            $table->string('city_of_creation')->nullable();
            $table->enum('availability', ['в наличии', 'продано'])->default('в наличии');

            $table->timestamps();

            // Внешние ключи
            $table->foreign('artist_id')->references('id')->on('artists')->onDelete('cascade');
            $table->foreign('gallery_id')->references('id')->on('galleries')->onDelete('set null');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('paintings');
    }
};
