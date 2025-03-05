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
            $table->id()->primary();

            $table->string('title');
            $table->text('description')->nullable();
            $table->uuid('artist_id');
            $table->uuid('gallery_id')->nullable();
            $table->uuid('category_id')->nullable();
            $table->string('technique')->nullable();
            $table->string('dimensions')->nullable();
            $table->decimal('price', 12)->nullable();
            $table->string('image_url')->nullable();
            $table->string('city_of_creation')->nullable();

            $table->enum('availability', ['в наличии', 'продано'])->default('в наличии');
            $table->timestamps();
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
