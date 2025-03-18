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
        Schema::create('painting_categories', function (Blueprint $table) {
            $table->unsignedBigInteger('painting_id');
            $table->unsignedBigInteger('category_id');

            $table->primary(['painting_id', 'category_id']);

            $table->foreign('painting_id')->references('id')->on('paintings')->onDelete('cascade');
            $table->foreign('category_id')->references('id')->on('categories')->onDelete('cascade');
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('painting_categories');
    }
};
